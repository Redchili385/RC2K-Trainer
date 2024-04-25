from locale import normalize
from time import sleep
import random
from datetime import datetime
import json

from botorch import fit_gpytorch_model
from gpytorch import ExactMarginalLogLikelihood
import torch
from LocalReadWriteMemory import ReadWriteMemory
from process import ensureWrite, ensureWrites, readFloat
from rallyProcess import RallyProcess, getBotParameters, getKeyByBotParameter, getProcessBotParameterValuesFromProcess, getProcessBotParameters, setProcessBotParametersToProcess
from rallyUtil import currentPlayerToPlayer0, getBotParametersBounds, getBotParametersByKey
from torchUtil import standardize, unnormalize
from util import parseJSON, readFile, selectMean
from gtbo.gaussian_process import robust_optimize_acqf
from gtbo.benchmarks import BoTorchFunctionBenchmark
from gtbo.gtbo import GTBO
from botorch.models import SingleTaskGP
from botorch.acquisition import UpperConfidenceBound
from botorch.test_functions.synthetic import SyntheticTestFunction, Ackley
import gin
import logging
import os

#Initial configuration
os.environ["CUDA_LAUNCH_BLOCKING"] = "1"
logging.basicConfig(level=logging.DEBUG)
logging.debug("DEBUG: RC2K Trainer Started")
random.seed(datetime.now().ctime())
torch.set_printoptions(threshold=10_000)
mapName = "Port_Soderick"
fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{mapName}.json"
numberOfRunsPerEvaluation = 2
#current_noise_std = 0.01/numberOfRunsPerEvaluation
current_noise_std = 0

#Opening Process because is seems always necessary in traner.py
process = RallyProcess("ral_botTraining_220424.exe")

#ParameterSetting
botParameters = getBotParameters()
botParameterByKey = getBotParametersByKey(botParameters)
botParametersBounds = getBotParametersBounds(botParameters)

def black_box_function(**args):
    scores = []
    for i in range(numberOfRunsPerEvaluation):
        scores.append(process.runStage(botParametersByKey, args))
    return selectMean(1, scores)

def setUpGame(process: RallyProcess):
    process.setBestParameters()
    process.ensureWriteInt32(process.pMaxWinTime, 3000000)
    process.ensureWriteInt32(process.pMaxWinTime2, 3000000)
    process.ensureWriteInt32(process.pFalseStartTime, 5000)
    
setUpGame(process)

# if os.path.isfile("./logs/logsBest_20240413_Port_Soderick.json"):
#     load_logs(optimizer, logs=["./logs/logsBest_20240413_Port_Soderick.json"])
# else:

def botParameterBoundsToTensor(botParameterBounds):
    tensorBounds = []
    for botParameterBound in botParameterBounds.values():
        min = float(botParameterBound[0])
        max = float(botParameterBound[1])
        tensorBounds.append([min, max])
    return torch.tensor(tensorBounds, dtype=torch.float32).transpose(0, 1)


def tensorToBotParameterValuesByKey(tensor: torch.Tensor, botParameters):
    botParameterValuesByKey = {}
    for (i, value) in enumerate(tensor):
        botParameter = botParameters[i]
        # print("botParameter")
        # print(botParameter)
        # print("value")
        # print(value)
        key = getKeyByBotParameter(botParameter)
        # print("key")
        # print(key)
        botParameterValuesByKey[key] = value.item()
    return botParameterValuesByKey

def botParameterValuesByKeyToTensor(botParameterValuesByKey, botParameters):
    tensor = []
    for botParameter in botParameters:
        key = getKeyByBotParameter(botParameter)
        tensor.append(botParameterValuesByKey[key])
    return torch.tensor(tensor, dtype=torch.float32)

def black_box_torch_function(input_tensor: torch.Tensor, base_tensor: torch.Tensor):
    # print("input_tensor")
    # print(input_tensor)
    sumTarget = torch.empty((0), dtype=torch.float32)
    for input_tensor_line in input_tensor:
        # print(input_tensor_line)
        # print("base_tensor")
        # print(base_tensor)
        input_tensor_size = input_tensor_line.shape[0]
        # print("input_tensor_size")
        # print(input_tensor_size)
        copied_base_tensor = base_tensor.clone().detach()
        copied_base_tensor[:input_tensor_size] = input_tensor_line[:input_tensor_size]
        # print("copied_base_tensor")
        # print(copied_base_tensor)
        botParameterValuesByKey = tensorToBotParameterValuesByKey(copied_base_tensor)
        target = black_box_function(**botParameterValuesByKey)
        targetTensor = torch.tensor([target], dtype=torch.float32)
        logStepValue(input_tensor_line, targetTensor)
        # print("sumTarget")
        # print(sumTarget)
        # print(targetTensor)
        sumTarget = torch.cat((sumTarget, targetTensor), dim=0)
    return sumTarget

def getInitialInputValuesTorch(process: RallyProcess):
    botParameterValuesByKey = process.getBotParameterValuesByKey(botParameterByKey)
    return botParameterValuesByKeyToTensor(botParameterValuesByKey, botParameters), botParameterValuesByKey

def getInitialValueTorch():
    botParameterValuesTensor, botParameterValuesByKey = getInitialInputValuesTorch(process)
    print("botParameterValuesTensor")
    print(botParameterValuesTensor)
    targetTensor = torch.tensor([black_box_function(**botParameterValuesByKey)], dtype=torch.float32)
    return botParameterValuesTensor, targetTensor

def getInitialValuesTorch(bounds: torch.Tensor):
    torchInitialValues, torchTarget = getInitialValueTorch()
    torchInitialValues = torchInitialValues.unsqueeze(0)
    torchTarget = torchTarget.unsqueeze(0)
    for bound in bounds:
        boundTarget = black_box_torch_function(bound)
        torchTarget = torch.cat((torchTarget, boundTarget.unsqueeze(0)), dim=0)
        torchInitialValues = torch.cat((torchInitialValues, bound.unsqueeze(0)), dim=0)
    return torchInitialValues, torchTarget

def getNextValuesTorch(initX, initY):
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
    newTarget = black_box_torch_function(candidatesToRun)
    return candidatesToRun, newTarget

def logStepValue(stepParams, target: torch.Tensor):
    file = open(fileToLogPath, "a")
    botParameterValues = tensorToBotParameterValuesByKey(stepParams)
    file.write(json.dumps({
        "target": target.item(),
        "params": botParameterValues
    }))
    file.write("\n")
    file.close()

#Setting bounds
initialBounds = botParameterBoundsToTensor(botParametersBounds)
print("initialBounds")
print(initialBounds)
print("initialBoundsSize")
print(initialBounds.shape[1])
initialInputValuesTorch, _ = getInitialInputValuesTorch()
print("initialInputValuesTorch")
print(initialInputValuesTorch)
boundsWindow = 0.005
unitBoundsAmplitude = 1.5
unitBounds = torch.cat((torch.zeros(initialBounds.shape[1]).unsqueeze(0), torch.ones(initialBounds.shape[1]).unsqueeze(0))).transpose(0, 1) * unitBoundsAmplitude - unitBoundsAmplitude/2
print(unitBounds)
print(initialInputValuesTorch.unsqueeze(1))
print("sum")
print(initialInputValuesTorch.unsqueeze(1) + unitBounds)
bounds = torch.clamp(initialInputValuesTorch.unsqueeze(1) + unitBounds, min=initialBounds[0].unsqueeze(1), max=initialBounds[1].unsqueeze(1))
#bounds = initialInputValuesTorch.unsqueeze(1) + unitBounds
#bounds = (initialBounds - initialInputValuesTorch)*boundsWindow + initialInputValuesTorch
print("bounds")
print(bounds)
transposedBounds = bounds.clone().detach().transpose(0, 1)
print("transposedBounds")
print(transposedBounds)
initialInputValuesTorch = torch.clamp(initialInputValuesTorch, min=transposedBounds[0], max=transposedBounds[1])
print("clampedInitialInputValuesTorch")
print(initialInputValuesTorch)

def startBoTorchBayesianOptimization():
    maxSteps = 500

    initX, initY = getInitialValuesTorch(bounds)
    for i in range(initX.shape[0]):
        logStepValue(initX[i], initY[i])

    for i in range(maxSteps):
        x, y = getNextValuesTorch(initX, initY)
        logStepValue(x, y)

        x = x.unsqueeze(0)
        y = y.unsqueeze(0)
        initX = torch.cat((initX, x), dim=0)
        initY = torch.cat((initY, y), dim=0)

gin.parse_config_file('default.gin')

class RallySynteticFunction(SyntheticTestFunction):
    def __init__(self, noise_std=current_noise_std, negate=True, **tkwargs):
        print("Init RallySynteticFunction")
        self.dim = bounds.shape[1]
        print("self.dim")
        print(self.dim)
        self.base_tensor = initialInputValuesTorch
        #print("self.base_tensor")
        #print(self.base_tensor)
        self._optimal_value = 0.30
        super().__init__(noise_std, negate, transposedBounds, **tkwargs)
        self.default = self.base_tensor

    def evaluate_true(self, X: torch.Tensor) -> torch.Tensor:
        # print("evaluate_true RallySynteticFunction X")
        # print(X)
        target =  black_box_torch_function(X, self.base_tensor)
        # print(target)
        return target

print(type(RallySynteticFunction))

class RallyBenchmark(BoTorchFunctionBenchmark):
    def __init__(self, **kwargs):
        logging.debug("Init RallyBenchmark")
        super().__init__(
            dim = bounds.shape[0],
            noise_std=current_noise_std,
            ub = transposedBounds[1],
            lb = transposedBounds[0],
            returns_noiseless=True,
            #effective_dim = bounds.shape[1],
            benchmark_func=RallySynteticFunction
        )
        self.default = initialInputValuesTorch

# benchmark = RallyBenchmark(
#     dim = bounds.shape[1],
#     ub = bounds[1],
#     lb = bounds[0],
#     noise_std=current_noise_std,
#     effective_dim = bounds.shape[1],
#     benchmark_func=RallySynteticFunction
# )

GTBO(
    benchmark=RallyBenchmark(),
    maximum_number_evaluations=500,
    number_initial_points=1,
    results_dir="./logs/",
    device="cuda",
    dtype='float32',
    logging_level='info',
    retrain_gp_from_scratch_every=100,
).run()



    