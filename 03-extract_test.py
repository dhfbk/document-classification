import os
import json
import tqdm
import logging
import pickle
import fasttext
import pandas as pd
import numpy as np
import random
import scipy
import argparse
import math

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import f1_score

parser = argparse.ArgumentParser(description='Save file for FastText.')
parser.add_argument("input_tint_folder", metavar="input-tint-folder", help="Folder with JSON files parsed by Tint")
parser.add_argument("input_file", metavar="input-file", help="JSON file with labels and IDs")
parser.add_argument("output_folder", metavar="output-folder", help="Output folder")
parser.add_argument("--ratio", help="Percentage of test data (default: 0.2)", type=float, default=0.2)

args = parser.parse_args()

log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

if not os.path.exists(args.output_folder):
    os.makedirs(args.output_folder)

testListName = os.path.join(args.output_folder, "testlist.txt")
testRatio = args.ratio

log.info("Loading JSON file")
with open(args.input_file, "r") as f:
    data = json.load(f)

trainSize = 0
testSize = 0
testList = []

classSizes = {}
testSizes = {}
isMultiLabel = False
for record in data:

    # Better to check this here, too
    tintFile = os.path.join(args.input_tint_folder, record['id'] + ".json")
    if not os.path.exists(tintFile):
        log.warning("File %s does not exist" % tintFile)
        continue

    if len(record['labels']) > 1:
        isMultiLabel = True
    else:
        for label in record['labels']:
            if not label in classSizes:
                classSizes[label] = 0
            classSizes[label] += 1

for label in classSizes:
    testSizes[label] = 0
    num = classSizes[label]
    if num > 1:
        testSizes[label] = math.ceil(testRatio * num)

random.shuffle(data)

log.info("Extracting texts")
for record in data:
    tintFile = os.path.join(args.input_tint_folder, record['id'] + ".json")
    if not os.path.exists(tintFile):
        log.warning("File %s does not exist" % tintFile)
        continue

    if len(record['labels']) == 0:
        log.warning("File %s has no labels, skipping" % tintFile)
        continue

    isTest = False
    if isMultiLabel:
        extract = random.uniform(0, 1)
        isTest = extract < testRatio
    else:
        if testSizes[record['labels'][0]] > 0:
            testSizes[record['labels'][0]] -= 1
            isTest = True

    if isTest:
        testList.append(record['id'])
        testSize += 1
    else:
        trainSize += 1

log.info("Saving test list")
with open(testListName, "w") as fw:
    for testID in testList:
        fw.write(testID)
        fw.write("\n")

log.info("Train size: %d" % trainSize)
log.info("Test size: %d" % testSize)
