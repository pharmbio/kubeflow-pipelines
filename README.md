# Kubeflow Pipelines repository
This repository hosts a collection of publicly available Kubeflow Pipeline projects for the Pharmb.io group. Within each project folder please provide a README describing the pipeline, instructions for building, deployment and running the pipelines.

## General Kubeflow Pipelines guide
Pipelines are created in python with the help of the kfpipelines DSL library, and generally the script can be run to build a pipeline tar archive. This archive can then be uploaded to a Kubeflow dashboard to run and interact with it. Various preconditions of Kubernetes environments (such as Volumes and Claims, Secrets etc.) that are expected should be documented and often can be solved in multiple ways across different Kubernetes clusters.