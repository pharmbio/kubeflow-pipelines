#!/bin/bash -e

checkpoint=$4
echo $4
if [[ "$checkpoint" ]]; then
    echo Checkpointing...
    mkdir -p /home/output/
    touch /home/output/bbbc014_labels.npy
    exit 0
fi

### preprocessing script

# 1 - ingestion
echo Copying images from NFS...
cp -rH /mnt/data/bbbc/BBBC014/BBBC014_v1_images /home/kensert_CNN/BBBC014_v1_images

# 2 - run kensert generate datasets
echo Copy complete, running code...
cd /home/kensert_CNN
python /home/kensert_CNN/generate_dataset_bbbc014.py
echo Code finished, moving images to output
#rm -rf /home/kensert_CNN/BBBC014_v1_images

# 3 - store output and prepare for downstream
mv -n images_bbbc014/ /mnt/data/workdir/
cp bbbc014_labels.npy /mnt/data/workdir/
cp bbbc014_labels.npy /home/output/
echo Output prepared, preprocess completed
