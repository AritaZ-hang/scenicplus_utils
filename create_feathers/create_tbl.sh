#!/bin/bash
for f in *fa ; 
do python /media/ggj/Guo-4T-C2/tools/OrthoFinder_source/tools/primary_transcript.py $f ; done
python /media/ggj/Guo-4T-C2/tools/OrthoFinder_source/orthofinder.py -f primary_transcripts/

#Script to add orthologue to motif2TF
/media/ggj/Guo-4T-C2/tools/fa/orthologuous.R
