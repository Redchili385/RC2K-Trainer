import logging

import torch

from rallyTorchTrainer import RallyTorchTrainer
from gtbo.benchmarks import BoTorchFunctionBenchmark
from botorch.test_functions.synthetic import SyntheticTestFunction
from gtbo.gtbo import GTBO

class RallyGTBOTrainer(RallyTorchTrainer):
  def __init__(self, process):
    super().__init__(process)
    #current_noise_std = 0.01/numberOfRunsPerEvaluation
    current_noise_std = 0
    outerSelf = self

    class RallySynteticFunction(SyntheticTestFunction):
      def __init__(self, noise_std=current_noise_std, negate=True, **tkwargs):
          print("Init RallySynteticFunction")
          self.dim = outerSelf.bounds.shape[1]
          print("self.dim")
          print(self.dim)
          self.base_tensor = outerSelf.initialInputValuesTorch
          #print("self.base_tensor")
          #print(self.base_tensor)
          self._optimal_value = 0.30
          super().__init__(noise_std, negate, outerSelf.transposedBounds, **tkwargs)
          self.default = self.base_tensor

      def evaluate_true(self, X: torch.Tensor) -> torch.Tensor:
          # print("evaluate_true RallySynteticFunction X")
          # print(X)
          target =  outerSelf.black_box_torch_function(X, self.base_tensor)
          # print(target)
          return target
      
    print(type(RallySynteticFunction))
      
    class RallyBenchmark(BoTorchFunctionBenchmark):
      def __init__(self, **kwargs):
          logging.debug("Init RallyBenchmark")
          super().__init__(
              dim = outerSelf.bounds.shape[0],
              noise_std=current_noise_std,
              ub = outerSelf.transposedBounds[1],
              lb = outerSelf.transposedBounds[0],
              returns_noiseless=True,
              #effective_dim = bounds.shape[1],
              benchmark_func=RallySynteticFunction
          )
          self.default = outerSelf.initialInputValuesTorch

    self.GTBO = GTBO(
        benchmark=RallyBenchmark(),
        maximum_number_evaluations=500,
        number_initial_points=1,
        results_dir="./logs/",
        device="cuda",
        dtype='float32',
        logging_level='info',
        retrain_gp_from_scratch_every=100,
    )
  
  def train(self):
    self.GTBO.run()

