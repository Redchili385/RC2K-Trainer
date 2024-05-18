from gpytorch import ExactMarginalLogLikelihood
import torch
from rallyTorchTrainer import RallyTorchTrainer
from torchUtil import normalize, standardize, unnormalize
from botorch.models import SingleTaskGP
from botorch import fit_gpytorch_model
from botorch.acquisition import UpperConfidenceBound
from gtbo.gaussian_process import robust_optimize_acqf


class RallySimpleTorchTrainer(RallyTorchTrainer):
  def __init__(self, process):
    super().__init__(process)
  
  def getNextValuesTorch(self, initX, initY):
    x, initXMin, initXMax = normalize(initX)
    y, _, _ = standardize(initY)
    print(x, y)
    singleModel = SingleTaskGP(x, y)
    mll = ExactMarginalLogLikelihood(singleModel.likelihood, singleModel)
    fit_gpytorch_model(mll)
    ucb = UpperConfidenceBound(singleModel, beta=0.1)
    singleBounds = torch.tensor([[0.0], [1.0]], dtype=torch.float32)
    bounds = torch.cat([singleBounds for _ in range(x.shape[1])], dim=1)

    candidates, _ = robust_optimize_acqf(
        acq_function=ucb,
        bounds=bounds,
        q=1,
    )
    candidatesToRun = unnormalize(candidates, initXMin, initXMax)[0]
    newTarget = self.black_box_torch_function(candidatesToRun)
    return candidatesToRun, newTarget
  
  def train(self):
    maxSteps = 500

    initX, initY = self.getInitialValuesTorch(self.bounds)
    for i in range(initX.shape[0]):
        self.logStepValue(initX[i], initY[i])

    for i in range(maxSteps):
        x, y = self.getNextValuesTorch(initX, initY)
        self.logStepValue(x, y)

        x = x.unsqueeze(0)
        y = y.unsqueeze(0)
        initX = torch.cat((initX, x), dim=0)
        initY = torch.cat((initY, y), dim=0)