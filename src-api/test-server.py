from os import path, environ, listdir
from transformers import pipeline
from fastapi import FastAPI, HTTPException, Header
from fastapi.staticfiles import StaticFiles
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from dotenv import load_dotenv
load_dotenv()

max_results = 100

models_path = environ.get("MODEL_PATH", "./models")
device = environ.get("DEVICE", "cpu")
language = environ.get("CLASSLANG", "it")
label_mappings_path = environ.get("LABEL_MAPPINGS_PATH", "./label_mappings")
id_label_path = environ.get("ID_LABEL_PATH", "./id2label.json")
mt_label_path = environ.get("MT_LABEL_PATH", "./mt_labels.json")
id_eu_path = environ.get("ID_EU_PATH", "./i2eu_id.json")
ui_path = environ.get("UI_PATH", "./dist")

models = {}
for p in listdir(models_path):
    config_file = path.join(models_path, p, "config.json")
    if path.exists(config_file):
        t = "euvoc"
        if p.startswith("ipzs"):
            t = "ipzs"
        models[p] = t

labels = {}
with open(id_label_path, "r", encoding="utf-8") as f:
    labels['ipzs'] = json.load(f)
with open(path.join(label_mappings_path, f"{language}.json"), "r", encoding="utf-8") as f:
    labels['euvoc'] = json.load(f)
if path.exists(path.join(label_mappings_path, f"{language}_do.json")):
    with open(path.join(label_mappings_path, f"{language}_do.json"), "r", encoding="utf-8") as f:
        d = json.load(f)
        for k in d:
            labels['euvoc'][k] = d[k]
if path.exists(path.join(label_mappings_path, f"{language}_mt.json")):
    with open(path.join(label_mappings_path, f"{language}_mt.json"), "r", encoding="utf-8") as f:
        d = json.load(f)
        for k in d:
            labels['euvoc'][k] = d[k]

parents = {}
if path.exists(mt_label_path):
    with open(mt_label_path, "r", encoding="utf-8") as f:
        parents = json.load(f)

mappings = {}
with open(id_eu_path, "r", encoding="utf-8") as f:
    mappings = json.load(f)

classifiers = {}
for modelName in models:
    print(f"Loading model {modelName}...")
    model_path = path.join(models_path, modelName)

    classifiers[modelName] = pipeline(
        'text-classification',
        model = model_path,
        tokenizer = model_path, 
        config = path.join(model_path, "config.json"),
        device = device,
        padding = True,
        truncation = True,
        top_k = None,
        max_length = 512)

print("Starting API...")
# Allow CORS for all origins
middleware = [
    Middleware(
        CORSMiddleware,
        allow_origins = ['*'],
        # allow_credentials=True, # uncomment this line if you want to allow credentials, but you have to set allow_origins to a list of allowed origins
        allow_methods = ['*'],
        allow_headers = ['*'],
        expose_headers = ['access-control-allow-origin'],
    )
]

app = FastAPI(middleware=middleware)
if path.exists(ui_path):
    app.mount("/ui", StaticFiles(directory=ui_path, html = True), name="ui")


# Define the request body. It should contain only a text field
class TextRequest(BaseModel):
    text: str = ""
    model: str
    title: str = ""
    top_k: int = 50
    threshold: float = 0.0
    greedy: bool = False

# Dummy endpoint to check if the API is running
@app.get("/api/models")
async def get_data():
    return models

# Endpoint to get the predictions for a text
@app.post("/api/predict")
async def post_data(request: TextRequest, Token: str = Header(None, convert_underscores=False)):

    if environ.get("AUTH_TOKEN") and Token != environ.get("AUTH_TOKEN"):
        raise HTTPException(status_code=500, detail="Wrong token header")

    text = request.text
    model = request.model
    title = request.title
    top_k = request.top_k
    threshold = request.threshold
    greedy = request.greedy

    # print(request)
    # print(Token)

    text = title + "\n" + text

    if len(text.strip()) == 0:
        raise HTTPException(status_code=400, detail="Empty text and title")

    if model not in classifiers:
        raise HTTPException(status_code=400, detail=f"Model '{model}' does not exist")

    t = models[model]
    these_labels = labels[t]
    predictions = classifiers[model](text)
    good_predictions = []
    i = 0
    for p in predictions[0]:
        p['description'] = these_labels[p['label']]
        if t == "ipzs":
            p['mapping'] = {}
            if p['label'] in mappings:
                p['mapping']['label'] = mappings[p['label']]
                if p['mapping']['label'] in labels['euvoc']:
                    p['mapping']['description'] = labels['euvoc'][p['mapping']['label']]
        else:
            if p['label'] in parents:
                p['mt'] = {
                    "label": parents[p['label']]
                }
                if parents[p['label']] in these_labels:
                    p['mt']["description"] = these_labels[parents[p['label']]]
                do_label = parents[p['label']][0:2]
                p['do'] = {
                    "label": do_label
                }
                if do_label in these_labels:
                    p['do']["description"] = these_labels[do_label]
        i += 1
        condition = i > top_k or threshold > p['score']
        if greedy:
            condition = i > top_k and threshold > p['score']
        if condition or i > max_results:
            break
        good_predictions.append(p)

    return good_predictions
