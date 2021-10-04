import os
import json
import logging
import tqdm
import csv
import re

parser = argparse.ArgumentParser(description='Save file for FastText.')
parser.add_argument("input_folder", metavar="input-folder", help="Folder containing skills_it.csv")
parser.add_argument("output_file", metavar="output-file", help="Output file")

args = parser.parse_args()

idPrefix = "esco-"

logging.basicConfig(level=logging.INFO)

allObjs = []

with open(os.path.join(args.input_folder, 'skills_it.csv')) as csvfile:
    csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
    next(csvreader, None)
    for row in csvreader:
        thisId = re.sub("http:.*/", "", row[1])
        title = row[4]
        description = row[12]
        text = title + "\n" + description

        thisObj = {}
        thisObj['text'] = text
        thisObj['id'] = idPrefix + thisId
        thisObj['labels'] = [thisId]
        allObjs.append(thisObj)

jsonString = json.dumps(allObjs, indent=4)
jsonFile = open(args.output_file, "w")
jsonFile.write(jsonString)
jsonFile.close()

