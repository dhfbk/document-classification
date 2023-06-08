# Document classification API

## Installation

Just run `pip install -r requirements.txt` to install all the libraries needed to run the scripts.

## Configuration

Before running the API, there are some environments variables you can set.

* `MODEL_PATH`: folder containing the BERT models (one for each subfolder, whose name
  must start with `euvoc-` or `ipzs-` to infer the corresponding label space) \[default: `./models`\]
* `LABEL_MAPPINGS_PATH`: folder including the JSON files (one per language, `it.json` for Italian)
  containing the descriptions of the EuroVoc labels \[default: `./label_mappings`\]
* `ID_LABEL_PATH`: path to the JSON file containing the descriptions of the IPZS
  labels \[default: `id2label.json`\]
* `ID_EU_PATH`: path to the JSON file containing the mappings between IPZS and EuroVoc codes
  \[default: `i2eu_id.json`\]

## Run the server

The server can be run with the command (or similar):

```
uvicorn test-server:app --host [HOST] --port [PORT]
```

with the desired `HOST` and `PORT`.
