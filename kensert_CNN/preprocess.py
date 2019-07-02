import kfp.dsl as dsl



class TrainerOp(dsl.ContainerOp):

  def __init__(self, name, cluster_name, train_data, eval_data,
               target, analysis, workers, rounds, output, is_classification=True):

    super(TrainerOp, self).__init__(
      name=name,
      image='pharmbio/pipelines-kensert-preprocess:test',
      arguments=[
          '--project', project,
          '--region', region,
          '--cluster', cluster_name,
          '--train', train_data,
          '--eval', eval_data,
          '--analysis', analysis,
          '--target', target,
          '--workers', workers,
          '--rounds', rounds,
          '--conf', config,
          '--output', output,
      ],
      file_outputs={'output': '/output.txt'})