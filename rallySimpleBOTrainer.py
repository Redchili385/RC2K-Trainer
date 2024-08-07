import random
from bayes_opt import BayesianOptimization, Events, JSONLogger, SequentialDomainReductionTransformer, UtilityFunction
from rallyTrainer import RallyTrainer


class RallySimpleBOTrainer(RallyTrainer):
  def __init__(self, process, initBotParameterValuesWithTargetList = None):
    super().__init__(process, initBotParameterValuesWithTargetList)
    self.bounds_transformer = SequentialDomainReductionTransformer(
        gamma_osc = 0.7,
        gamma_pan = 4.0,
        eta= 0.90,
        minimum_window=0.0
    )
    self.optimizer = BayesianOptimization(
      f=self.black_box_function,
      pbounds=self.botParametersBounds,
      random_state=random.randint(0, 0xffffffff),
      verbose=2,
      bounds_transformer=self.bounds_transformer,
      allow_duplicate_points=True,
    )

    for botParameterValues in self.initBotParameterValuesList:
      self.optimizer.probe(
          params=botParameterValues,
          lazy=True,
      )

    logger = JSONLogger(path=self.fileToLogPath)
    self.optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)

    self.optimizer.set_gp_params(alpha=1e-3, n_restarts_optimizer=500)
    self.acquisition_function = UtilityFunction(kind="ucb", kappa=1e2, kappa_decay=0.80)
  
  def train(self):
    self.optimizer.maximize(
      acquisition_function=self.acquisition_function,
      init_points=0,
      n_iter=10000,
    )

    