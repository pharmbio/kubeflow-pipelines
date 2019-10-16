#!/bin/bash -e

checkpoint=$4

if [[ "$checkpoint" == "true" ]]; then
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
python /home/kensert_CNN/train.py
echo Training complete, preparing outputs...

# 3 - store output and prepare for downstream
mkdir -p /mnt/data/workdir/models
mv *.h5 /mnt/data/workdir/models
echo Outputs prepared, finished training