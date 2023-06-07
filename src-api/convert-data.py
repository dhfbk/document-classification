import json
import argparse
import csv
import re

parser = argparse.ArgumentParser(description='Convert format.')
parser.add_argument("input_file", help="Input JSON file.")
parser.add_argument("output_file", help="Output TSV file.")
args = parser.parse_args()

input_data = {}
with open(args.input_file, "r") as f:
    input_data = json.load(f)

excelData = []
excelHeader = ["ID", "Title", "IPZS", "Mappings"]
for i in range(10):
    excelHeader.append(f"EV {i + 1} label")
    excelHeader.append(f"EV {i + 1} desc")
    excelHeader.append(f"EV {i + 1} acc")
excelData.append(excelHeader)

for d in input_data:
    dt = input_data[d]
    title = re.sub(r"\s+", " ", dt['title'])
    thisRow = [d, title, "-".join(dt['ipzs']), "-".join(dt['mapping'])]
    for e in dt['eurovoc_base']:
        thisRow.append(e)
        thisRow.append(dt['eurovoc_base'][e]['term'].strip())
        thisRow.append(str(round(dt['eurovoc_base'][e]['score'], 3)).replace(".", ","))
    excelData.append(thisRow)

with open(args.output_file, "w") as fw:
    tsv_writer = csv.writer(fw, delimiter='\t')
    for e in excelData:
        tsv_writer.writerow(e)
