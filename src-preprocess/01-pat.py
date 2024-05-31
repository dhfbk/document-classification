import os
import json
import logging
import csv
import re
import argparse

parser = argparse.ArgumentParser(description='Save file for training.')
parser.add_argument("input_file", metavar="input-file", help="CSV file containing actions")
parser.add_argument("output_file", metavar="output-file", help="Output file")
parser.add_argument("--min_for_label", default=10, metavar="num", help="Minimum examples for each label")
parser.add_argument("--skip_no_description", help="Skip documents without description", action="store_true")
parser.add_argument("--use_scope", help="Use scope (macroambito) instead of class", action="store_true")

args = parser.parse_args()

idPrefix = "pat-"

# log = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

tmpObj = {}
with open(args.input_file) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    for row in csvreader:
        thisId = row[2]
        if args.use_scope:
            label = idPrefix + row[1]
        else:
            label = idPrefix + row[3]
        title = row[4].strip()
        description = row[6].strip()
        if args.skip_no_description and description == "":
            continue
        if label not in tmpObj:
            tmpObj[label] = []
        text = title + "\n" + description

        thisObj = {}
        thisObj['text'] = text
        thisObj['id'] = thisId
        thisObj['labels'] = [label]
        tmpObj[label].append(thisObj)

label_count = 0
document_count = 0

allObjs = []
for label in tmpObj:
    if len(tmpObj[label]) >= args.min_for_label:
        for d in tmpObj[label]:
            allObjs.append(d)
        document_count += len(tmpObj[label])
        label_count += 1

logging.info(f"Documents: {document_count} - Labels: {label_count}")

jsonString = json.dumps(allObjs, indent=4)
jsonFile = open(args.output_file, "w")
jsonFile.write(jsonString)
jsonFile.close()

