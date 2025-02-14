import random
from bayes_opt import BayesianOptimization, Events, JSONLogger, SequentialDomainReductionTransformer, UtilityFunction
from rallyTrainer import RallyTrainer


class RallySimpleBOTrainer(RallyTrainer):
  def __init__(self, process, initBotParameterValuesWithTargetList = None):
    super().__init__(process, initBotParameterValuesWithTargetList)
    baseIterations = 20  #100+ iterations starts to be very expensive time wise with 25 dimensions
    self.bounds_transformer = SequentialDomainReductionTransformer(
        gamma_osc = 0.7,
        gamma_pan = 1.0,
        eta=pow(0.1, 1/baseIterations), #Expected 2.5 base iterations to find Int8 best parameters, 10 to find Int32 best parameters (N dimensional)
        minimum_window=0.0
    )
    self.optimizer = BayesianOptimization(
      f=self.black_box_function,
      pbounds=self.trainingBotParametersBounds,
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
    self.acquisition_function = UtilityFunction(kind="ucb", kappa=1e1, kappa_decay=pow(0.08, 1/baseIterations)) #For 2.5 base iterations => kappa is reduced from 1e1 to 1e-2 (Reduced 1000 times) 
  
  def train(self):
    self.optimizer.maximize(
      acquisition_function=self.acquisition_function,
      init_points=0,
      n_iter=10000,
    )

    