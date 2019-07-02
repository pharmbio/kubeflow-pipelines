#!/bin/bash -e

### preprocessing script

# 1 - ingestion
echo Copying images from NFS...
cp -rH /mnt/data/BBBC014/BBBC014_v1_images /home/kensert_CNN/

# 2 - run kensert generate datasets
echo Copy complete, running code...
python /home/kensert_CNN/generate_dataset_bbbc014.py
#echo Code finished, clearing images...
#rm -rf /home/kensert_CNN/BBBC014_v1_images

# 3 - store output and prepare for downstream
ls images_bbbc014 >> /output/images.txt
cp bbbc014_labels.npy /output/