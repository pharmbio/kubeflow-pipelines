#!/bin/bash -e

checkpoint=$4

if [[ "$checkpoint" ]]; then
    echo Checkpointing...
    mkdir -p /home/output/kensert_CNN
    touch /home/output/kensert_CNN/predictions_bbbc014
    exit 0
fi

### training script
echo $WORKFLOW_NAME
echo $0 $1 $2
# 1 - ingestion
echo Copying images from NFS...
cp -r /mnt/data/workdir/images_bbbc014 /home/kensert_CNN/
cp -r /mnt/data/workdir/bbbc014_labels.npy /home/kensert_CNN/

# 2 - run training script
echo Copy complete, running code...
cd /home/kensert_CNN
python /home/kensert_CNN/run_model_bbbc014.py
echo Training complete, preparing outputs...
ls

#echo Code finished, clearing images...
#rm -rf /home/kensert_CNN/BBBC014_v1_images

# 3 - store output and prepare for downstream
#ls images_bbbc014 >> /home/output/images.txt
#cp bbbc014_labels.npy /home/output/
mkdir -p /home/output/kensert_CNN
cp predictions_bbbc014* /home/output/kensert_CNN/predictions_bbbc014
mkdir -p /mnt/data/workdir/models
mv saved_model.h5 /mnt/data/workdir/models
echo Outputs prepared, finished training