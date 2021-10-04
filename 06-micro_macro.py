import logging
import argparse

from sklearn.metrics import f1_score
from sklearn.preprocessing import MultiLabelBinarizer

parser = argparse.ArgumentParser(description='Get micro/macro.')
parser.add_argument("pred_file", metavar="pred-file", help="Predictions file")
parser.add_argument("gold_file", metavar="gold-file", help="Gold file")
parser.add_argument("--prob-threshold", help="Probability threshold (default: 0.5)", type=float, default=0.5)

args = parser.parse_args()

probThreshold = args.prob_threshold

logging.basicConfig(level=logging.INFO)

y_true = []
y_pred = []

with open(args.pred_file) as f:
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        parts = line.split()
        y = []
        hasProb = False
        if len(parts) > 1 and not parts[1].startswith("__label__"):
            hasProb = True

        if hasProb:
            for i in range(1, len(parts), 2):
                if len(y) == 0:
                    y.append(parts[i - 1])
                else:
                    if float(parts[i]) > probThreshold:
                        y.append(parts[i - 1])
        else:
            for part in parts:
                if part.startswith("__label__"):
                    y.append(part)
        y_pred.append(y)

with open(args.gold_file) as f:
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue
        parts = line.split()
        y = []
        for part in parts:
            if part.startswith("__label__"):
                y.append(part)
        y_true.append(y)

m = MultiLabelBinarizer().fit(y_true)

macro_f1_score = f1_score(m.transform(y_true), m.transform(y_pred), average='macro')
micro_f1_score = f1_score(m.transform(y_true), m.transform(y_pred), average='micro')

print("Macro:", macro_f1_score)
print("Micro:", micro_f1_score)
