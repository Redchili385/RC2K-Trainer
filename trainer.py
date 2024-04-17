from time import sleep
from bayes_opt import BayesianOptimization, UtilityFunction
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from bayes_opt import SequentialDomainReductionTransformer
import os.path
import random
from datetime import datetime
from LocalReadWriteMemory import ReadWriteMemory
from processUtil import ensureWrite, ensureWrites, readFloat
from rallyProcess import getBotParameters, getBotParametersBounds, getProcessBotParameterValuesFromProcess, getProcessBotParameters, getProcessBotParametersByAddress, setProcessBotParametersToProcess
from rallyUtil import currentPlayerToPlayer0
from util import selectMean
#from GTBO import GTBO

random.seed(datetime.now().ctime())

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
    for i in range(2):
        scores.append(runStage(args))
    return selectMean(1, scores)

def setUpGame():
    ensureWrite(pMaxWinTime, 3000000, process)
    ensureWrite(pMaxWinTime2, 3000000, process)
    ensureWrite(pFalseStartTime, 5000, process)
    #ensureWrite(pBotCalculated2Strength2, 0x40000000)
    #fmul dword ptr [00601028]
    

setUpGame()

bounds_transformer = SequentialDomainReductionTransformer(
    gamma_osc = 0.7,
    gamma_pan = 4.0,
    eta= 0.95,
    minimum_window=0.0
)
#print(botParametersBounds["0x71beba_float32"][0])
#print(type(botParametersBounds["0x71beba_float32"][0]))

optimizer = BayesianOptimization(
    f=black_box_function,
    pbounds=botParametersBounds,
    random_state=random.randint(0, 0xffffffff),
    verbose=2,
    bounds_transformer=bounds_transformer,
    allow_duplicate_points=True,
)

# if os.path.isfile("./logs/logsBest_20240413_Port_Soderick.json"):
#     load_logs(optimizer, logs=["./logs/logsBest_20240413_Port_Soderick.json"])
# else:
optimizer.probe(
    params=getProcessBotParameterValuesFromProcess(processBotParametersByAddress, process),
    lazy=True,
)

mapName = "Port_Soderick"
logger = JSONLogger(path=f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{mapName}", reset=True)
optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)

optimizer.set_gp_params(alpha=1e-3, n_restarts_optimizer=500)
acquisition_function = UtilityFunction(kind="ucb", kappa=1e1, kappa_decay=0.87)
optimizer.maximize(
    acquisition_function=acquisition_function,
    init_points=0,
    n_iter=10000,
)