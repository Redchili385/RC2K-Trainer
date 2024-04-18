from time import sleep
import random
from datetime import datetime
import json

from botorch import fit_gpytorch_model
from gpytorch import ExactMarginalLogLikelihood
import torch
from LocalReadWriteMemory import ReadWriteMemory
from processUtil import ensureWrite, ensureWrites, readFloat
from rallyProcess import getBotParameters, getBotParametersBounds, getKeyByBotParameter, getProcessBotParameterValuesFromProcess, getProcessBotParameters, getProcessBotParametersByAddress, setProcessBotParametersToProcess
from rallyUtil import currentPlayerToPlayer0
from util import selectMean
from gtbo.gaussian_process import robust_optimize_acqf
from botorch.models import SingleTaskGP
from botorch.acquisition import UpperConfidenceBound

random.seed(datetime.now().ctime())
torch.set_printoptions(threshold=10_000)

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

def black_box_function(**args):
    scores = []
    for i in range(1):
        scores.append(runStage(args))
    return selectMean(1, scores)

def setUpGame():
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
    return torch.tensor(tensorBounds, dtype=torch.float64).transpose(0, 1)


def tensorToBotParameterValuesByAddress(tensor):
    paramValuesByAddress = {}
    for (i, value) in enumerate(tensor):
        botParameter = botParameters[i]
        key = getKeyByBotParameter(botParameter)
        paramValuesByAddress[key] = value.item()
    return paramValuesByAddress

def botParameterValuesByAddressToTensor(paramValuesByAddress):
    initialValues = []
    for processBotParameter in processBotParameters:
        key = getKeyByBotParameter(processBotParameter.botParameter)
        initialValues.append(paramValuesByAddress[key])
    return torch.tensor([initialValues], dtype=torch.float64)

def black_box_torch_function(input_tensor):
    paramValuesByAddress = tensorToBotParameterValuesByAddress(input_tensor)
    target = black_box_function(**paramValuesByAddress)
    return torch.tensor([target], dtype=torch.float64)

def getInitialValuesTorch(bounds: torch.Tensor):
    valuesByAddress = getProcessBotParameterValuesFromProcess(processBotParametersByAddress, process)
    torchInitialValues = botParameterValuesByAddressToTensor(valuesByAddress)
    torchTarget = torch.tensor([[black_box_function(**valuesByAddress)]], dtype=torch.float64)
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
    singleBounds = torch.tensor([[0.0], [1.0]], dtype=torch.float64)
    bounds = torch.cat([singleBounds for _ in range(x.shape[1])], dim=1)

    candidates, _ = robust_optimize_acqf(
        acq_function=ucb,
        bounds=bounds,
        q=1,
    )
    candidatesToRun = unnormalize(candidates, initXMin, initXMax)[0]
    newTarget = black_box_torch_function(candidatesToRun)
    return candidatesToRun, newTarget

def logStepValue(stepParams, target, fileToLogPath):
    file = open(fileToLogPath, "a")
    botParameterValues = tensorToBotParameterValuesByAddress(stepParams)
    file.write(json.dumps({
        "target": target.item(),
        "params": botParameterValues
    }))
    file.write("\n")
    file.close()


mapName = "Port_Soderick"
bounds = botParameterBoundsToTensor(botParametersBounds)
initX, initY = getInitialValuesTorch(bounds)
fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{mapName}.json"
for i in range(initX.shape[0]):
    logStepValue(initX[i], initY[i], fileToLogPath)

maxSteps = 500
for i in range(maxSteps):
    x, y = getNextValuesTorch(initX, initY)
    logStepValue(x, y, fileToLogPath)

    x = x.unsqueeze(0)
    y = y.unsqueeze(0)
    initX = torch.cat((initX, x), dim=0)
    initY = torch.cat((initY, y), dim=0)

    