import kfp.dsl as dsl
import kfp.gcp as gcp
from kubernetes.client.models import V1SecretKeySelector, V1EnvVar
#from kfp.onprem import mount_pvc
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

def set_resources_dict(resource_spec_string, container:dsl.ContainerOp.container=None):
    #resource_spec = None
    #resource_spec_string.value:
    resource_spec = loads(
        resource_spec_string.value if resource_spec_string.value else
        '{"memory":{"request":"2Gi", "limit":"4Gi"}, "cpu":{"request":"2", "limit":"4"}}')
    if container:
        container.set_memory_request(resource_spec.get("memory",{}).get("request"))
        container.set_memory_limit(resource_spec.get("memory",{}).get("limit"))
        container.set_cpu_request(resource_spec.get("cpu",{}).get("request"))
        container.set_cpu_limit(resource_spec.get("cpu",{}).get("limit"))
        gpus=resource_spec.get("gpus", 0)
        if int(gpus) > 0:
            container.set_gpu_limit(gpus)
        return container
    return None

@dsl.pipeline(
  name='Kensert_CNN_test',
  description='Testing a CNN workflow in kfpipelines'
)
def cnn_workflow(
    model_type: dsl.PipelineParam=dsl.PipelineParam(name="model_type", value="Inception_v3"),
    artifact_bucket: dsl.PipelineParam=dsl.PipelineParam(name="artifact_bucket", value="kensert_CNN"),
    workspace_name: dsl.PipelineParam=dsl.PipelineParam(name="workspace_name", value="kensert_CNN"),
    #memory_limit: dsl.PipelineParam=dsl.PipelineParam(name="memory_limit", value="4Gi"),
    #memory_request: dsl.PipelineParam=dsl.PipelineParam(name="memory_request", value="1Gi"),
    #cpu_limit: dsl.PipelineParam=dsl.PipelineParam(name="cpu_limit", value="1000m"),
    #cpu_request: dsl.PipelineParam=dsl.PipelineParam(name="cpu_request", value="4000m"),
    #gpus: dsl.PipelineParam=dsl.PipelineParam(name="gpus", value="0")
    #preprocessing_resources: dsl.PipelineParam=dsl.PipelineParam(name="preprocessing_resources",value="{'default':'value'}")
):
    artifact_location = dsl.ArtifactLocation.s3(
        bucket=artifact_bucket,
        endpoint="minio-service:9000",
        insecure=True,
        access_key_secret=V1SecretKeySelector(name="mlpipeline-minio-artifact", key="accesskey"),
        secret_key_secret=V1SecretKeySelector(name="mlpipeline-minio-artifact", key="secretkey")
    )

    preprocessing = dsl.ContainerOp(
        name="preprocessing",
        image="pharmbio/pipelines-kensert-preprocess:test",
        arguments=[ "--model-type" , model_type],

        container_kwargs={"image_pull_policy": "Always", "env":[V1EnvVar(name="WORKFLOW_NAME",value=workspace_name)]},
        file_outputs={"labels":"/home/output/bbbc014_labels.npy"}
    )
    preprocessing.apply(mount_pvc(pvc_name="external-images-kubeflow-pvc",volume_name="external-images-kubeflow-pv",volume_mount_path="/mnt/data"))
    preprocessing.apply(mount_pvc(pvc_name="kubeflow-workdir-pvc",volume_name="kubeflow-workdir-pv",volume_mount_path="/mnt/data/workdir",volume_sub_path=workspace_name))
    set_resources(memory_req="4Gi", memory_lim="8Gi", cpu_req="2", cpu_lim="4", container=preprocessing.container)
    #set_resources_dict(preprocessing_resources, container=preprocessing.container)
    #preprocessing.container.set_pull_image_policy("Always")
    #set_resources(memory_req=memory_request.value, memory_lim=memory_limit.value, cpu_req=cpu_request.value, cpu_lim=cpu_limit.value, container=preprocessing.container)

    training = dsl.ContainerOp(
        name="training",
        image="pharmbio/pipelines-kensert-training:test",
        arguments=[ "--model-type" , model_type],
        container_kwargs={"image_pull_policy": "Always", "env":[V1EnvVar(name="WORKFLOW_NAME",value=workspace_name)]},
        file_outputs={"prediction_accuracy":"/home/output/kensert_CNN/predictions_bbbc014"}
    )
    training.apply(mount_pvc(pvc_name="kubeflow-workdir-pvc",volume_name="kubeflow-workdir-pv",volume_mount_path="/mnt/data/workdir",volume_sub_path=workspace_name))
    set_resources(memory_req="4Gi", memory_lim="8Gi", cpu_req="2", cpu_lim="4", gpus="1", container=training.container)
    training.after(preprocessing)


if __name__ == '__main__':
    import kfp.compiler as compiler
    compiler.Compiler().compile(cnn_workflow, __file__ + '.tar.gz')