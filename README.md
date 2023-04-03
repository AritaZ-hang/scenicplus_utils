# scenicplus_utils

## Target
1. 创建其他物种的regions_vs_motifs_ranking.feather文件
2. scenicplus & cisTopic & cisTarget Ray 无法启动 的解决办法
3. 尽量增添对其他物种的支持

## 目前进度
1. run_homer.py & run_cistarget.py 对 ensembl物种的支持
2. utils.py load_motif_annotations函数 消除潜在NAN值对 pd data frame合并的影响
3. enhancer_to_gene.py get_search_space函数 更改判断顺序 & 区分UCSC assembly 和 Ensembl assembly参数（因为有的基因组，在UCSC和Ensembl的名字不一样）
4. 另外请确保RNA gene_name & TF_list TF name是一致的
