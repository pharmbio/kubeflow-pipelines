import kfp.dsl as dsl
import kfp.gcp as gcp
from kubernetes.client.models import V1SecretKeySelector, V1EnvVar
from kubernetes import client as k8s_client
from json import loads

def mount_pvc(pvc_name='pipeline-claim', volume_name='pipeline', volume_mount_path='/mnt/pipeline', volume_sub_path=None):
    """
        Modifier function to apply to a Container Op to simplify volume, volume mount addition and
        enable better reuse of volumes, volume claims across container ops.
        Usage:
            train = train_op(...)
            train.apply(mount_pvc('claim-name', 'pipeline', '/mnt/pipeline'))
    """
    def _mount_pvc(task):
        from kubernetes import client as k8s_client
        local_pvc = k8s_client.V1PersistentVolumeClaimVolumeSource(claim_name=pvc_name)
        return (
            task
                .add_volume(
                    k8s_client.V1Volume(name=volume_name, persistent_volume_claim=local_pvc)
                )
                .add_volume_mount(
                    k8s_client.V1VolumeMount(mount_path=volume_mount_path, name=volume_name, sub_path=volume_sub_path)
                )
        )
    return _mount_pvc


def set_resources(memory_req=None, memory_lim=None, cpu_req=None, cpu_lim=None, gpus="0", container:dsl.ContainerOp.container=None):
    if container:
        container.set_memory_request(memory_req)
        container.set_memory_limit(memory_lim)
        container.set_cpu_request(cpu_req)
        container.set_cpu_limit(cpu_lim)
        if int(gpus) > 0:
            container.set_gpu_limit(gpus)
        return container
    else:
        return None

@dsl.pipeline(
  name='Kensert_CNN_test',
  description='Testing a CNN workflow in kfpipelines'
)
def cnn_workflow(
    ### inputs to pipeline
    model_type: dsl.PipelineParam=dsl.PipelineParam(name="model_type", value="Inception_v3"),
    artifact_bucket: dsl.PipelineParam=dsl.PipelineParam(name="artifact_bucket", value="kensert_CNN"),
    checkpoint_preprocess: dsl.PipelineParam=dsl.PipelineParam(name="checkpoint_preprocess", value="false"),
    checkpoint_training: dsl.PipelineParam=dsl.PipelineParam(name="checkpoint_training", value="false"),
    checkpoint_evaluation: dsl.PipelineParam=dsl.PipelineParam(name="checkpoint_evaluation", value="false"),
    workspace_name: dsl.PipelineParam=dsl.PipelineParam(name="workspace_name", value="kensert_CNN"),
    model_repo: dsl.PipelineParam=dsl.PipelineParam(name="model_repo", value=""),
):

    ### preprocessing step
    preprocessing = dsl.ContainerOp(
        name="preprocessing",
        image="pharmbio/pipelines-kensert-preprocess:test",
        arguments=[ "--model-type" , model_type, "--checkpoint", checkpoint_preprocess],
        # NOTE: arguments from pipeline not utilized in training script yet
        container_kwargs={"image_pull_policy": "Always", "env":[V1EnvVar(name="WORKFLOW_NAME",value=workspace_name)]},
        file_outputs={"labels":"/home/output/bbbc014_labels.npy"}
    )
    ### add resource definitions, pvc mounts etc.
    preprocessing.apply(mount_pvc(pvc_name="external-images-kubeflow-pvc",volume_name="external-images-kubeflow-pv",volume_mount_path="/mnt/data"))
    preprocessing.apply(mount_pvc(pvc_name="kubeflow-workdir-pvc",volume_name="kubeflow-workdir-pv",volume_mount_path="/mnt/data/workdir",volume_sub_path=workspace_name))
    set_resources(memory_req="4Gi", memory_lim="8Gi", cpu_req="2", cpu_lim="4", container=preprocessing.container)

    ### training step
    training = dsl.ContainerOp(
        name="training",
        image="pharmbio/pipelines-kensert-training:test",
        arguments=[ "--model-type" , model_type,  "--checkpoint", checkpoint_training],
        container_kwargs={"image_pull_policy": "Always", "env":[V1EnvVar(name="WORKFLOW_NAME",value=workspace_name)]}
    )
    ### set order (after preprocessing), add pvc and resource definitions
    training.apply(mount_pvc(pvc_name="kubeflow-workdir-pvc",volume_name="kubeflow-workdir-pv",volume_mount_path="/mnt/data/workdir",volume_sub_path=workspace_name))
    set_resources(memory_req="4Gi", memory_lim="8Gi", cpu_req="2", cpu_lim="4", gpus="1", container=training.container)
    training.after(preprocessing)

     ### evaluation step
    evaluation = dsl.ContainerOp(
        name="evaluation",
        image="pharmbio/pipelines-kensert-evaluation:test",
        # NOTE: arguments from pipeline not utilized in training script yet
        arguments=[ "--model-type" , model_type,  "--checkpoint", checkpoint_evaluation],
        container_kwargs={"image_pull_policy": "Always", "env":[V1EnvVar(name="WORKFLOW_NAME",value=workspace_name)]}
        #file_outputs={"prediction_accuracy":"/home/output/kensert_CNN/predictions_bbbc014"}
    )
    ### set order (after training), add pvc and resource definitions
    evaluation.apply(mount_pvc(pvc_name="kubeflow-workdir-pvc",volume_name="kubeflow-workdir-pv",volume_mount_path="/mnt/data/workdir",volume_sub_path=workspace_name))
    set_resources(memory_req="1Gi", memory_lim="4Gi", cpu_req="1", cpu_lim="2", gpus="1", container=evaluation.container)
    evaluation.after(training)

    ### model building step
    model_building = dsl.ContainerOp(
        name="model_building",
        image="pharmbio/pipelines-kensert-building:test",
        arguments=[ ],
        container_kwargs={"image_pull_policy": "Always", "env":[V1EnvVar(name="WORKFLOW_NAME",value=workspace_name), V1EnvVar(name="MODEL_REPO",value=model_repo)]}
    )
    ### set order (after evaluation), add secrets, socket (hostpath pv mount), pvc and resource definitions
    model_building.apply(mount_pvc(pvc_name="kubeflow-workdir-pvc",volume_name="kubeflow-workdir-pv",volume_mount_path="/home/models",volume_sub_path=(str(workspace_name) + "/models")))
    docker_socket_volume = k8s_client.V1Volume(name='dockervol-pv', host_path=k8s_client.V1HostPathVolumeSource(path='/var/run/docker.sock'))
    docker_credentials_volume = k8s_client.V1Volume(name="dockercreds", secret=k8s_client.V1SecretVolumeSource(secret_name="dockercreds"))
    model_building.add_pvolumes({"/var/run/docker.sock":docker_socket_volume, "/root/.docker/":docker_credentials_volume})
    set_resources(memory_req="1Gi", memory_lim="2Gi", cpu_req="1", cpu_lim="2", container=model_building.container)
    model_building.after(evaluation)

### build pipeline when executing python script
if __name__ == '__main__':
    import kfp.compiler as compiler
    compiler.Compiler().compile(cnn_workflow, __file__ + '.tar.gz')