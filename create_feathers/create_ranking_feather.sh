#BSUB -q normal
#BSUB -J create_ranking_feather
#BSUB -o %J.out
#BSUB -e %J.err
#BSUB -R "span[ptile=10]"
#BSUB -n 48

## 提供的文件列表：
## workdir: 工作目录
## genomefa：目标物种的基因组文件
## motif_dir：cisTarget提供的motif collections文件路径，下载后解压获得
## motif_list：目的motif list的名字
## output：输出文件路径及前缀名
## da.final.bed: 是cisTopic获得的每一细胞类型的DA peak的总和；理论可以用call peak or ChIP-seq数据替代。

workdir=/share/home/guoguoji/RAWDATA/ZS/scenicplus
genomefa=$workdir/danRer11.fa
motif_dir=$workdir/v10nr_clust_public/singletons
motif2tf=$workdir/zf_motif2tf_orthologuous.tbl
motif_list=$workdir/danRer_motif_list.txt
output=$workdir/dr11

source /share/home/guoguoji/JiaqiLi/tools/anaconda3/bin/activate create_cistarget_databases
create_cistarget_databases_dir='/share/home/guoguoji/RAWDATA/ZS/scenicplus/create_cisTarget_databases-master'

## fetch motif name from motif folder
ls $motif_dir | sed -e 's/.cb//' > $motif_list

## Get fasta sequences..
bedtools getfasta -fi $genomefa -bed $workdir/da.final.bed > $workdir/consensus_regions.fa #DA regions bed

## feather base creation
/share/home/guoguoji/RAWDATA/ZS/scenicplus/create_cisTarget_databases-master/create_cistarget_motif_databases.py \
--fasta $workdir/consensus_regions.fa \
--motifs_dir $motif_dir \
--motifs $motif_list \
--threads 48 \
--output $output \
-l

echo "Creating rankings DB files ..."
/share/home/guoguoji/RAWDATA/ZS/scenicplus/convert_motifs_or_tracks_vs_regions_or_genes_scores_to_rankings_cistarget_dbs.py -i $workdir/dr11.motifs_vs_regions.scores.feather -s 555
echo "Done."
echo "ALL DONE."
