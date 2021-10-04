import requests
import json
import os
import tqdm
import logging
import argparse

parser = argparse.ArgumentParser(description='Parse files with Tint.')
parser.add_argument("input_file", metavar="input-file", help="JSON complete file with labels and IDs")
parser.add_argument("output_folder", metavar="output-folder", help="Output folder")
parser.add_argument("--tint_url", help="Tint URL", type=str, default="http://dh-server.fbk.eu:8016/tint")

args = parser.parse_args()

logging.basicConfig(level=logging.INFO)

def runTint(sentence_text):
    # requires args['tint-url']
    myobj = {'text' : sentence_text.strip()}
    x = requests.post(args.tint_url, data = myobj)
    data = json.loads(x.text)
    return data

if not os.path.exists(args.output_folder):
    os.mkdir(args.output_folder)

logging.info("Loading texts")
with open(args.input_file, "r") as f:
    data = json.load(f)

errors = []

logging.info("Running Tint")
pbar = tqdm.tqdm(data, smoothing=0.5, maxinterval=1)
for record in pbar:
    text = record['text']
    thisId = record['id']
    pbar.set_description(thisId)
    outputFile = os.path.join(args.output_folder, thisId + ".json")
    if os.path.exists(outputFile):
        continue
    try:
        parsedData = runTint(text)
    except Exception:
        errors.append(thisId)
        continue
    with open(outputFile, 'w') as fw:
        fw.write(json.dumps(parsedData, indent = 4))

logging.info("Errors: " + str(errors))
