# CNN example pipeline
This is an example pipeline based on an article from A. Kensert, with the code available at https://github.com/pharmbio/kensert_CNN/tree/model-serving

## Pipeline description
The pipeline consists of 4 different stages; data preparation, training, validation and model-serving packaging. Each stage is built as a container, with all Dockerfiles and related bash scripts available in the subfolders. In short, the original machine learning code is treated as a black box and the shell scripts in the Docker containers prepare files and execute the python code as-is from the source repo. At the final stage, a Docker image with the resulting trained model packaged as a servable function with OpenFaaS is created and pushed to a target repository, which the user defines when running the pipeline.

## Building pipeline
Ensure that the kfp python package is [installed](https://www.kubeflow.org/docs/pipelines/sdk/install-sdk/#install-the-kubeflow-pipelines-sdk). Simply run the pipeline script:

`python pipeline.py`

This results in a file `pipeline.py.tar.gz` or an update to the already existing file, which is the file to be uploaded in the Kubeflow Pipelines dashboard

## Kubernetes preconditions
This pipeline depends on a few volumes and secrets to function.

PVC:
* `external-images-kubeflow-pvc` - intended as the volume claim with required data to run, in this case the BBBC014 image dataset is available under the structure `bbbc/BBBC014/BBBC014_v1_images/<BMP images>`
* `kubeflow-workdir-pvc` - intended as a persisting working directory for the pipeline, any intermediate results are stored here and this allows for caching and checkpointing the work

PV:
* `dockervol-pv` - a PV for the host machine docker socket, in order to build docker images in the container without root access (further reading [here](https://estl.tech/accessing-docker-from-a-kubernetes-pod-68996709c04b), see "_Accessing the Docker Socket_"), should be a hostPath volume pointing to `/var/run/docker.sock`

Secret:
* `dockercreds` - a secret containing the key `config.json` with the credentials from a `.docker/config.json` file that can authenticate to the desired docker repository

NOTE: These should already exist per default in the Pharmbio Kubeflow setup and you should not need to worry about this unless deploying this elsewhere.

## Running the pipeline
From the Kubeflow Pipelines UI, create a run using this pipeline (optionally create an experiment to categorize the run, but experiments are not linked to pipelines, only runs are). The input parameters currently include options for specifying model and artifact repository, neither of which are implemented to do anything, checkpointing for the different stages (should be set to _true_ to skip the computation on the respective stage and use available cached results), the workspace name which dictates the folder name within the working directory to be used for the intermediary results, and finally the url to the docker repository to host the model-server image.