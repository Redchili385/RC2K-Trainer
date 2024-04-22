from time import sleep
import random
from datetime import datetime
import json

from botorch import fit_gpytorch_model
from gpytorch import ExactMarginalLogLikelihood
import torch
from LocalReadWriteMemory import ReadWriteMemory
from processUtil import ensureWrite, ensureWrites, readFloat
from rallyProcess import getBotParameters, getKeyByBotParameter, getProcessBotParameterValuesFromProcess, getProcessBotParameters, setProcessBotParametersToProcess
from rallyUtil import currentPlayerToPlayer0, getBotParametersBounds, getProcessBotParametersByAddress
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

os.environ["CUDA_LAUNCH_BLOCKING"] = "1"

logging.basicConfig(level=logging.DEBUG)
logging.debug("DEBUG: RC2K Trainer Started")

random.seed(datetime.now().ctime())
torch.set_printoptions(threshold=10_000)

mapName = "Port_Soderick"
fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{mapName}.json"

rwm = ReadWriteMemory()
process = rwm.get_process_by_name("ral.exe")
process.open()

#pTime = process.get_pointer(0x70f474)
#time = process.read(pTime)
#print({'time': time})

#pEnterKeyCode = process.get_pointer(0x4F6AD4)
#process.write(pEnterKeyCode, 0x1c)
#pEnterKey = process.get_pointer(0x4F6AF8)
#process.write(pEnterKey, 0xff)

pWinTime = process.get_pointer(currentPlayerToPlayer0(0x71A080)) #timeStppedCarToWin
pCompletedSquares = process.get_pointer(currentPlayerToPlayer0(0x71A068))
pCentisecondsSinceStart = process.get_pointer(currentPlayerToPlayer0(0x71A060))
pCentisecondsSinceLevelLoaded = process.get_pointer(currentPlayerToPlayer0(0x719FEC))
pMaxWinTime = process.get_pointer(0x436a13)
pMaxWinTime2 = process.get_pointer(0x436a39)
pFalseStartTime = process.get_pointer(0x43b9f4)
pValidTrackPosition = process.get_pointer(0x70f3ec+0x94)
pMaximumTrackPosition = process.get_pointer(0x623640)
engineDamageAddress = 0x70f3ec+0*0xfe0+0x2B8
#pBotCalculated2Strength2 = process.get_pointer(0x71bfa4)
#pTriggerGameStart = process.get_pointer(currentPlayerToPlayer0(0x719FF4))
#pCurrentGearNumber = process.get_pointer(currentPlayerToPlayer0(0x71A1AC))
#pCurrentAccelerationOnPedal = process.get_pointer(currentPlayerToPlayer0(0x719FF0))

botParameters = getBotParameters()
processBotParameters = getProcessBotParameters(process)
processBotParametersByAddress = getProcessBotParametersByAddress(processBotParameters)

botParametersBounds = getBotParametersBounds(botParameters)

def resetCarOnStage():
    writes = []
    writes.append([pCompletedSquares, 0])
    writes.append([pWinTime, 0])
    if process.read(pCentisecondsSinceStart) > 0:
        writes.append([pCentisecondsSinceStart, -1000])
    writes.append([pCentisecondsSinceLevelLoaded, 0])
    ensureWrites(writes, process)
    #print("Car Reseted")

def runStage(args):
    #print(args)
    print("Start")
    setProcessBotParametersToProcess(processBotParametersByAddress, args, process)
    resetCarOnStage()
    while(True):
        winTime = process.read(pWinTime)
        if winTime > 0:
            break
        centisecondsSinceStart = process.read(pCentisecondsSinceStart)
        maximumTrainingSessionTime = 100 * 60 * 15
        if(centisecondsSinceStart > maximumTrainingSessionTime and centisecondsSinceStart < 0x3FFFFFFF):
            print("End2")
            validTrackPosition = process.read(pValidTrackPosition)
            maximumTrackPosition = process.read(pMaximumTrackPosition)
            engineDamage = readFloat(engineDamageAddress, process)
            return (6000/maximumTrainingSessionTime) * (validTrackPosition / maximumTrackPosition) * (1 - engineDamage)
        sleep(0.1)
    time = process.read(pCentisecondsSinceStart)
    #print(time)
    print("End")
    return 6000/time

numberOfRunsPerEvaluation = 1
#current_noise_std = 0.01/numberOfRunsPerEvaluation
current_noise_std = 0
def black_box_function(**args):
    scores = []
    for i in range(numberOfRunsPerEvaluation):
        scores.append(runStage(args))
    return selectMean(1, scores)

def setBestParameters(process):
    logsBestString = readFile("./logs/logs_202404220414_Port_Soderick.json")
    logsBestStrings = logsBestString.split("\n")
    logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]
    bestLog = logsBestList[120]
    setProcessBotParametersToProcess(getProcessBotParametersByAddress(getProcessBotParameters(process)), bestLog["params"], process)

def setUpGame():
    setBestParameters(process)
    ensureWrite(pMaxWinTime, 3000000, process)
    ensureWrite(pMaxWinTime2, 3000000, process)
    ensureWrite(pFalseStartTime, 5000, process)
    #ensureWrite(pBotCalculated2Strength2, 0x40000000)
    #fmul dword ptr [00601028]
    

setUpGame()

#print(botParametersBounds["0x71beba_float32"][0])
#print(type(botParametersBounds["0x71beba_float32"][0]))

# if os.path.isfile("./logs/logsBest_20240413_Port_Soderick.json"):
#     load_logs(optimizer, logs=["./logs/logsBest_20240413_Port_Soderick.json"])
# else:

def standardize(Y):
    stddim = -1 if Y.dim() < 2 else -2
    Y_std = Y.std(dim=stddim, keepdim=True)
    Y_std = Y_std.where(Y_std >= 1e-9, torch.full_like(Y_std, 1.0))
    Y_mean = Y.mean(dim=stddim, keepdim=True)
    return (Y - Y_mean) / Y_std, Y_mean, Y_std

def unstandardize(Y, Y_mean, Y_std):
    return Y * Y_std + Y_mean

def normalize(i: torch.Tensor):
    min = i.min(dim=0)[0]
    max = i.max(dim=0)[0]
    print("min, max")
    print(min, max)
    return (i - min) / (max - min), min, max

#print(normalize(torch.tensor([[1.0, 2.0, 3.0], [4.0, 5.0, 6.0], [8.0, 10.0, 12.0]], dtype=torch.float64)))

def unnormalize(i, min, max):
    return i * (max - min) + min

def botParameterBoundsToTensor(botParameterBounds):
    tensorBounds = []
    for botParameterBound in botParameterBounds.values():
        min = float(botParameterBound[0])
        max = float(botParameterBound[1])
        tensorBounds.append([min, max])
    return torch.tensor(tensorBounds, dtype=torch.float32).transpose(0, 1)


def tensorToBotParameterValuesByAddress(tensor):
    paramValuesByAddress = {}
    for (i, value) in enumerate(tensor):
        botParameter = botParameters[i]
        # print("botParameter")
        # print(botParameter)
        # print("value")
        # print(value)
        key = getKeyByBotParameter(botParameter)
        # print("key")
        # print(key)
        paramValuesByAddress[key] = value.item()
    return paramValuesByAddress

def botParameterValuesByAddressToTensor(paramValuesByAddress):
    initialValues = []
    for processBotParameter in processBotParameters:
        key = getKeyByBotParameter(processBotParameter.botParameter)
        initialValues.append(paramValuesByAddress[key])
    return torch.tensor(initialValues, dtype=torch.float32)

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
        paramValuesByAddress = tensorToBotParameterValuesByAddress(copied_base_tensor)
        target = black_box_function(**paramValuesByAddress)
        targetTensor = torch.tensor([target], dtype=torch.float32)
        logStepValue(input_tensor_line, targetTensor)
        # print("sumTarget")
        # print(sumTarget)
        # print(targetTensor)
        sumTarget = torch.cat((sumTarget, targetTensor), dim=0)
    return sumTarget

def getInitialInputValuesTorch():
    valuesByAddress = getProcessBotParameterValuesFromProcess(processBotParametersByAddress, process)
    return botParameterValuesByAddressToTensor(valuesByAddress), valuesByAddress

def getInitialValueTorch():
    torchInitialValues, valuesByAddress = getInitialInputValuesTorch()
    print("torchInitialValues")
    print(torchInitialValues)
    torchTarget = torch.tensor([black_box_function(**valuesByAddress)], dtype=torch.float32)
    return torchInitialValues, torchTarget

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

def logStepValue(stepParams, target):
    file = open(fileToLogPath, "a")
    botParameterValues = tensorToBotParameterValuesByAddress(stepParams)
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
initialInputValuesTorch, _ = getInitialInputValuesTorch()
print("initialInputValuesTorch")
print(initialInputValuesTorch)
boundsWindow = 0.005
bounds = (initialBounds - initialInputValuesTorch)*boundsWindow + initialInputValuesTorch
print("bounds")
print(bounds)
transposedBounds = bounds.clone().detach().transpose(0, 1)
print("transposedBounds")
print(transposedBounds)

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
            dim = bounds.shape[1],
            noise_std=current_noise_std,
            ub = bounds[1],
            lb = bounds[0],
            returns_noiseless=True,
            #effective_dim = bounds.shape[1],
            benchmark_func=RallySynteticFunction
        )
        self.default, _ = getInitialInputValuesTorch()

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



    