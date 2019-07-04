#!/bin/bash -e

### preprocessing script

# 1 - ingestion
echo Copying images from NFS...
cp -rH /mnt/data/bbbc/BBBC014/BBBC014_v1_images /home/kensert_CNN/BBBC014_v1_images

# 2 - run kensert generate datasets
echo Copy complete, running code...
cd /home/kensert_CNN
python /home/kensert_CNN/generate_dataset_bbbc014.py
#echo Code finished, clearing images...
#rm -rf /home/kensert_CNN/BBBC014_v1_images

# 3 - store output and prepare for downstream
ls images_bbbc014 >> /home/output/images.txt
cp bbbc014_labels.npy /home/output/