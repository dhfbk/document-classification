#!/bin/bash

types=(goodTokens allLemmas allTokens)
# types=(allLemmas)
bys=(by_document by_label)

if [ -z "$1" ]
  then
    echo "No argument supplied"
    exit 1
fi

FOLDER=$1

for type in "${types[@]}"; do
  echo "***" $type
  echo "***" unfiltered
  ./fastText-0.9.2/fasttext supervised -input $FOLDER/${type}_unfiltered.train.txt -output $FOLDER/${type}_unfiltered_model -epoch 100 -lr 0.5 -loss one-vs-all -wordNgrams 2
  ./fastText-0.9.2/fasttext test $FOLDER/${type}_unfiltered_model.bin $FOLDER/${type}_unfiltered.test.txt -1 0.5
  ./fastText-0.9.2/fasttext predict-prob $FOLDER/${type}_unfiltered_model.bin $FOLDER/${type}_unfiltered.test.txt -1 > $FOLDER/${type}_unfiltered.results.txt
  python scripts/06-micro_macro.py $FOLDER/${type}_unfiltered.results.txt $FOLDER/${type}_unfiltered.test.txt
  for b in "${bys[@]}"; do
    echo "***" $b
    ./fastText-0.9.2/fasttext supervised -input $FOLDER/${type}_${b}_filtered.train.txt -output $FOLDER/${type}_${b}_filtered_model -epoch 100 -lr 0.5 -loss one-vs-all -wordNgrams 2
    ./fastText-0.9.2/fasttext test $FOLDER/${type}_${b}_filtered_model.bin $FOLDER/${type}_${b}_filtered.test.txt -1 0.5
    ./fastText-0.9.2/fasttext predict-prob $FOLDER/${type}_${b}_filtered_model.bin $FOLDER/${type}_${b}_filtered.test.txt -1 > $FOLDER/${type}_${b}_filtered.results.txt
    python scripts/06-micro_macro.py $FOLDER/${type}_${b}_filtered.results.txt $FOLDER/${type}_${b}_filtered.test.txt
  done
done
