#!/bin/bash

for file in $1*; do #in * ... should that be this?-> $1/*
    if [ -f "$file" ];  then
        fname=`basename $file`
        echo $fname
        python3 lemmatize.py $2 hfst ./languageSpecificAuxiliaryFiles/otw/pos_glosses/pos_regex.txt ./languageSpecificAuxiliaryFiles/otw/pos_glosses/RV_otw2eng.txt $file foo -c ../../nishDocProcessing/debugging/textReviewFiles/notes/${fname/otweng/notes} -o ../../nishDocProcessing/debugging/textReviewFiles/interlinearizations/${fname/otweng.txt/analyzed.json} -d
    fi
done

##make the analysis file
#cat $4 | awk -F'\t' '{print $4}' > nu.txt
#python3 word_per_line.py nu.txt | hfst-lookup $1 -q > tmp.txt
#
#
##do the rest of the processing in the python script ($2=pos tags, $3=dictionary $4 text $5 translation
#python3 lemmatize.py $1 hfst $2 $3 $4 $5 -a tmp.txt
#
#rm tmp.txt
#rm nu.txt
