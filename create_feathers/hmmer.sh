#!/bin/bash

## 用hmmer & pfam-A database扫一遍目标物种的蛋白组fasta序列，获得同源基因列表
hmmsearch --tblout /media/ggj/Guo-4T-C2/fa/cistarget_db/hmmerout.txt --cpu 8 /media/ggj/Guo-4T-C2/tools/Pfam-A.hmm /media/ggj/Guo-4T-C2/fa/cistarget_db/Danio_rerio.GRCz11.pep.all.fa
