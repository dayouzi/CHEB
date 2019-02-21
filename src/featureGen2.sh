echo $1
#python Feature.py -b $1
#used for mix books!!!
#cat ../../test/$1/$1.features | awk '{if($1==2){$1=1} for (i=1;i<NF;++i) printf "%s",$i"\t"; print $NF }' > ../../test/$1/$1.features_binary
cat ../../test/$1/$1.features_org | awk 'BEGIN{FS="\t";rank=0;pre=""}{if(pre!=$1){rank=rank+1;pre=$1}$1=rank; printf "%s", $3"\t"$1"\t"; for(i=4;i<NF;++i) printf "%s",$i"\t";print $NF }' > ../../test/$1/$1.features_id

cat ../../test/$1/$1.features_org | awk 'BEGIN{FS="\t";rank=0;pre=""}{if(pre!=$1){rank=rank+1;pre=$1}$1=rank;if($3==2){$3=1} printf "%s", $3"\t"$1"\t"; for(i=4;i<NF;++i) printf "%s",$i"\t";print $NF }' > ../../test/$1/$1.features_binary_id

cat ../../test/$1/$1.features_org_0 | awk 'BEGIN{FS="\t";rank=0;pre=""}{if(pre!=$1){rank=rank+1;pre=$1; print pre"\t"rank}}' > ../../test/$1/$1.qid_secTitle_0
cat ../../test/$1/$1.features_org_1 | awk 'BEGIN{FS="\t";rank=0;pre=""}{if(pre!=$1){rank=rank+1;pre=$1; print pre"\t"rank}}' > ../../test/$1/$1.qid_secTitle_1
cat ../../test/$1/$1.features_org_2 | awk 'BEGIN{FS="\t";rank=0;pre=""}{if(pre!=$1){rank=rank+1;pre=$1; print pre"\t"rank}}' > ../../test/$1/$1.qid_secTitle_2
#python prepro.py -b $1

sh fileGen.sh $1


