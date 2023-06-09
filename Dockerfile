FROM node:18-alpine AS VueImage

WORKDIR /app/frontend

COPY ./src-ui/package.json  /app/frontend/

RUN npm install --no-optional

COPY ./src-ui ./

RUN npm run build


FROM python:3.9

WORKDIR /code

COPY ./src-api/requirements.txt /code/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./src-api/test-server.py /code/test-server.py

COPY --from=VueImage ./app/frontend/dist/. ./dist/.

ENV MODEL_PATH=/data/models
ENV LABEL_MAPPINGS_PATH=/data/label_mappings
ENV ID_LABEL_PATH=/data/id2label.json
ENV ID_EU_PATH=/data/i2eu_id.json

CMD ["uvicorn", "test-server:app", "--proxy-headers", "--host", "0.0.0.0", "--port", "80"]