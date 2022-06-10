import argparse

parser = argparse.ArgumentParser(description='Save file for FastText.')
parser.add_argument("input_folder", metavar="input-folder", help="Folder containing JSON files")
parser.add_argument("input_file", metavar="input-file", help="File atti_SG_materie.csv")
parser.add_argument("output_file", metavar="output-file", help="Output file")
parser.add_argument("--output_stats", metavar="file", help="Output file with statistics")
parser.add_argument("--limit", metavar="num", help="Limit to skip labels (default: 0)", default=10, type=int)
parser.add_argument("--use_all_text", action="store_true")

args = parser.parse_args()

useAllText = args.use_all_text

import os
import json
import logging
import tqdm
import csv
import re
from datetime import datetime

idPrefix = "ipzs-ml-"
if useAllText:
    idPrefix = "ipzsc-"

limit = args.limit

logging.basicConfig(level=logging.INFO)
csvfilename = args.input_file

codePatt = re.compile("([^_]+_[^_]+)_([^_]+)_([^_]+)\.json")

dayIndex = {}
index = {}

for root, subFolder, files in os.walk(args.input_folder):
    for item in files:
        if item.endswith(".json") :
            fileNamePath = str(os.path.join(root,item))
            m = codePatt.match(item)
            if m:
                if m.group(1) in index:
                    logging.info(m.group(1) + " already exists")
                    logging.info(fileNamePath + " --- " + index[m.group(2)])
                index[m.group(1)] = fileNamePath
            else:
                logging.error("ERR: " + item)

allObjs = {}
count = {}
error_number = 0

with open(csvfilename, "r") as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(csvreader, None)
    for row in csvreader:
        day = row[1]
        code = row[0]
        category = row[2]
        d = datetime.strptime(day.lower(), "%d-%b-%y").date()
        code = datetime.strftime(d, "%Y%m%d") + "_" + code
        if code not in index:
            # logging.error("%s not in index" % code)
            error_number += 1
            continue

        if code not in allObjs:
            allObjs[code] = {}
            with open(index[code], "r") as f:
                data = json.load(f)

                texts = []
                titolo = data['metadati']['titoloDoc']
                titolo = re.sub(r"\n", " ", titolo)
                titolo = re.sub(r" +", " ", titolo)
                texts.append(titolo)

                if useAllText:
                    for element in data['articolato']['elementi']:
                        for subElement in element['elementi']:
                            text = subElement['testo']
                            text = re.sub(r"\n", " ", text)
                            text = re.sub(r" +", " ", text)
                            texts.append(text)

                allObjs[code]['text'] = " ".join(texts)
                allObjs[code]['id'] = idPrefix + code
                allObjs[code]['labels'] = []

        if category not in count:
            count[category] = 0
        count[category] += 1

        allObjs[code]['labels'].append(category)

if args.output_stats:
    with open(args.output_stats, "w") as fw:
        fw.write(json.dumps(count, indent=4))

logging.info("Errors: " + str(error_number))
logging.info("Objects before pruning: " + str(len(allObjs)))
newObjs = {}
if limit > 1:
    for code in allObjs:
        thisRecordLabels = allObjs[code]['labels']
        okLabels = [x for x in thisRecordLabels if (x in count and count[x] >= limit)]
        if len(okLabels) > 0:
            newObjs[code] = allObjs[code]
            newObjs[code]['labels'] = okLabels
else:
    newObjs = allObjs

logging.info("Objects after pruning: " + str(len(newObjs)))
jsonString = json.dumps(newObjs, indent=4)
jsonFile = open(args.output_file, "w")
jsonFile.write(jsonString)
jsonFile.close()

