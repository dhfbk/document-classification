import argparse

parser = argparse.ArgumentParser(description='Save file for FastText.')
parser.add_argument("--tint_port", metavar="port", help="Tint port", type=int, default=8012)
parser.add_argument("--tint_host", metavar="host", help="Tint host", default="localhost")
parser.add_argument("port", metavar="port", help="Port", type=int)
parser.add_argument("fasttext_model", metavar="model-file", help="FastText model file (bin)")
parser.add_argument("atti_file", metavar="atti-file", help="File atti_SG_materie.csv")

args = parser.parse_args()

csvfilename = args.atti_file

url = "http://" + args.tint_host + ":" + str(args.tint_port) + "/tint"
limit = 0.01

from http.server import BaseHTTPRequestHandler, HTTPServer
import logging
import urllib
import requests
import json
import fasttext
import numpy
import csv

class S(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        text = post_data.decode('utf-8')
        # text = text.replace("%0D", "")
        # mylist = urllib.parse.parse_qs(text)
        # myobj = {'text' : mylist['text']}
        input_data = json.loads(text)
        x = requests.post(url, data = input_data["text"])
        data = json.loads(x.text)

        limit = float(input_data["precision"])

        self.send_response(200)
        self.send_header('Content-type', 'text/json')
        self.end_headers()
        res = model.predict(data['document_classification'], k=-1)
        out = {}
        out['topics'] = {}
        out['words'] = data['document_classification']
        for i in range(len(res[0])):
            if res[1][i] > limit:
                title = res[0][i].replace('__label__', "")
                title += " - " + materie_dict[title]
                out['topics'][title] = res[1][i]
        ret = bytes(json.dumps(out), 'UTF-8')
        self.wfile.write(ret)

def run(server_class=HTTPServer, handler_class=S, port=8208):
    logging.basicConfig(level=logging.INFO)
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    logging.info('Starting httpd...\n')
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()
    logging.info('Stopping httpd...\n')

if __name__ == '__main__':
    materie_dict = {}
    with open(csvfilename, "r") as csvfile:
        csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        next(csvreader, None)
        for row in csvreader:
            materie_dict[row[2]] = row[3]
    model = fasttext.load_model(args.fasttext_model)
    run(port=args.port)
