from os import path, environ
from transformers import pipeline
from fastapi import FastAPI, HTTPException, Header
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json

from dotenv import load_dotenv
load_dotenv()

models = {
    "euvoc": "euvoc",
    "euvoc-s1": "euvoc",
    "euvoc-s3": "euvoc",
    "euvoc-sg": "euvoc",
    "ipzs-s1": "ipzs",
    "ipzs-s3": "ipzs",
    "ipzs-sg": "ipzs"
}
models_path = environ.get("MODEL_PATH", "./models")
device = environ.get("DEVICE", "cpu")
language = environ.get("CLASSLANG", "it")
label_mappings_path = environ.get("LABEL_MAPPINGS_PATH", "./label_mappings")
id_label_path = environ.get("ID_LABEL_PATH", "./id2label.json")
id_eu_path = environ.get("ID_EU_PATH", "./i2eu_id.json")

labels = {}
with open(id_label_path, "r", encoding="utf-8") as f:
    labels['ipzs'] = json.load(f)
with open(path.join(label_mappings_path, f"{language}.json"), "r", encoding="utf-8") as f:
    labels['euvoc'] = json.load(f)

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

# Define the request body. It should contain only a text field
class TextRequest(BaseModel):
    text: str = ""
    model: str
    title: str = ""
    top_k: int = 10
    threshold: float = 0.0
    greedy: bool = False

# Dummy endpoint to check if the API is running
@app.get("/")
async def get_data():
    return {"message": "Welcome to Mordor!"}

# Endpoint to get the predictions for a text
@app.post("/api")
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
        i += 1
        condition = i > top_k or threshold > p['score']
        if greedy:
            condition = i > top_k and threshold > p['score']
        if condition:
            break
        good_predictions.append(p)

    return good_predictions
