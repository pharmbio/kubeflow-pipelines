#!/bin/bash -e

checkpoint=$4

if [[ "$checkpoint" == "true" ]]; then
    echo Checkpointing...

    exit 0
fi

### evaluation script

# 1 - ingestion
echo Copying images from NFS...
cp -r /mnt/data/workdir/images_bbbc014 /home/kensert_CNN/
cp -r /mnt/data/workdir/bbbc014_labels.npy /home/kensert_CNN/
cp -r /mnt/data/workdir/models/*.h5 /home/kensert_CNN/

# 2 - run evaluation script
echo Copy complete, running code...
cd /home/kensert_CNN
python /home/kensert_CNN/evaluation.py
export EVALUATION_PASSED=$(python /home/check_pass.py)
echo $EVALUATION_PASSED
echo Evaluation complete, preparing outputs...

# 3 - store output and prepare for downstream
if [[ "$EVALUATION_PASSED" == "true" ]]; then
    echo Evaluation passed, will build model
    exit 0
else
    echo Evaluation did not pass, will not build model!
    exit 1
fi