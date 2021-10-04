import xml.sax
import html
import re
import os
import json
import hashlib
import unidecode
import logging
import codecs
import tqdm
import argparse

parser = argparse.ArgumentParser(description='Save file for FastText.')
parser.add_argument("input_folder", metavar="input-folder", help="Input folders with 'Scheda XX' and txt files")
parser.add_argument("output_file", metavar="output-file", help="Output file")

args = parser.parse_args()

myre = re.compile("Scheda ([0-9\.]+)")
idPrefix = "wemapp-"

logging.basicConfig(level=logging.INFO)

def walkdir(folder):
    """Walk through every files in a directory"""
    for dirpath, dirs, files in os.walk(folder):
        for filename in files:
            path = os.path.join(dirpath, filename)
            if path.lower().endswith(".txt"):
                yield path

allObjs = []

logging.info("Loading files")
filescount = 0
for file in walkdir(args.input_folder):
    filescount += 1

logging.info("File count: " + str(filescount))

for file_path in tqdm.tqdm(walkdir(args.input_folder), total=filescount):

        m = myre.findall(file_path)
        if len(m) == 0:
            continue

        label = m[0]

        result = hashlib.md5(bytearray(file_path, "UTF-8"))
        file_path_normalized = unidecode.unidecode(file_path)
        compressed_filename = re.sub("[^a-zA-Z0-9]", "_", file_path_normalized)
        compressed_filename = re.sub("__Modelli_Scheda_[0-9]+_", "", compressed_filename)
        compressed_filename = result.hexdigest() + "-" + compressed_filename[:200] + ".json"

        encoding = "utf-8"

        try:
            text = codecs.open(file_path, 'r', encoding).read()
        except UnicodeDecodeError:
            try:
                encoding = "Windows-1252"
                text = codecs.open(file_path, 'r', encoding).read()
            except UnicodeDecodeError:
                encoding = "latin1"
                text = codecs.open(file_path, 'r', encoding).read()

        thisObj = {}
        thisObj['text'] = text
        thisObj['id'] = idPrefix + compressed_filename
        thisObj['labels'] = [label]
        thisObj['encoding'] = encoding
        allObjs.append(thisObj)

jsonString = json.dumps(allObjs, indent=4)
jsonFile = open(args.output_file, "w")
jsonFile.write(jsonString)
jsonFile.close()

