# parse export_materie dump, containing following files: s1.csv, s3.csv, SG.csv, direttive-recepimenti.csv
# or, alternatively, a single file
# Since column names were not consistent, following column header have been renamed
# direttive-recepimenti.csv: REDAZ_S2 --> REDAZ
# s1.csv: MCODMAT --> MATERIA
# Since column names do not appear in the same order across files, the getFields function retrieves target names and their index

import os, json, logging, csv, argparse, pprint
from collections import Counter

logging.basicConfig(level=logging.INFO)

parser = argparse.ArgumentParser(description='Parse export-materie dump.')
parser.add_argument("input_folder", metavar="input-folder", help="Folder containing export files (csv).")
parser.add_argument("output_folder", metavar="output-folder", help="Output folder.")
parser.add_argument("-limit", metavar="limit", default=10, help="Min class occurrence threshold.")
parser.add_argument("-fname", metavar="fname", default=None, help="Name of specific file (series) to process.")
args = parser.parse_args()


def getFields(fields, targets=['REDAZ', 'TITOLO', 'MATERIA']):
    """
    given a set of field names and a list representing the document header,
    returns a mapping dictionary {'FIELDNAME': index_in_header}
    """
    mapping = {}
    for fieldname in targets:
        if fieldname in fields:
            mapping[fieldname] = fields.index(fieldname)
    assert len(mapping) == len(targets)
    return mapping

doc_types = {
    's1.csv': 's1',
    's3.csv': 's3',
    'SG.csv': 'sg',
    'direttive-recepimenti.csv': 'dr'
}


# Processing
idPrefix = "ipzs-"
filelist = os.listdir(args.input_folder) if not args.fname else [args.fname]
output = {}

for file in filelist:
    if file.endswith('.csv'):
        obj_count = 0
        logging.info("Processing " + file)
        
        with open(args.input_folder+file, 'r', encoding='ISO-8859-1') as csvfile:
            
            reader = csv.reader((line.replace('\0',' ') for line in csvfile), delimiter=',', quotechar='"') # NULL char in file
            headers = next(reader)
            field_map = getFields(headers)
            
            for row in reader:
                text = row[field_map['TITOLO']].replace("\n", " ").strip(" ")
                text = " ".join(text.split()) # remove all duplicate whitespaces
                ident = idPrefix+row[field_map['REDAZ']]
                mat = row[field_map['MATERIA']]
                dtype = doc_types[file]

                if ident not in output:
                    output[ident] = {"text": text, "labels": [mat], "dtype": dtype}
                    obj_count += 1
                else:
                    output[ident]["labels"].append(mat)
        logging.info("Found " + str(obj_count) + " objects.")
        
        
all_objs = [{"id": k, "text": v["text"], "labels": v["labels"], "dtype": v["dtype"]} for k,v in output.items()]
logging.info("Collected " + str(len(all_objs)) + " objects.")

logging.info("Removing under-threshold labels...")
all_labels = [obj['labels'] for obj in all_objs]
label_count = Counter(lab for labs in all_labels for lab in labs)
for obj in all_objs:
    obj['labels'] = [lab for lab in obj['labels'] if label_count[lab] > args.limit] # remove under-threshold labels

all_objs = [obj for obj in all_objs if len(obj['labels']) > 0] # remove now unlabelled objects
logging.info(str(len(all_objs)) + " objects left.")

logging.info("Writing to file.")
if not os.path.exists(args.output_folder):
    os.mkdir(args.output_folder)

if args.fname is None:
    json.dump(all_objs, open(args.output_folder+"01-expmat.json", 'w'), indent=4)
else:
    doctype = doc_types[args.fname]
    json.dump(all_objs, open(args.output_folder+"01-expmat_"+doctype+".json", 'w'), indent=4)