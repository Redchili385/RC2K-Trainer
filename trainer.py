from time import sleep
from LocalReadWriteMemory import ReadWriteMemory
from bayes_opt import BayesianOptimization, UtilityFunction
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from bayes_opt import SequentialDomainReductionTransformer
import os.path
import random
from datetime import datetime
from processUtil import ensureWrite, ensureWrites
from rallyProcess import getBotParameters, getBotParametersBounds, setBotParameters
from rallyUtil import currentPlayerToPlayer0
from util import selectMean

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
#pBotCalculated2Strength2 = process.get_pointer(0x71bfa4)
#pTriggerGameStart = process.get_pointer(currentPlayerToPlayer0(0x719FF4))
#pCurrentGearNumber = process.get_pointer(currentPlayerToPlayer0(0x71A1AC))
#pCurrentAccelerationOnPedal = process.get_pointer(currentPlayerToPlayer0(0x719FF0))

botParameters = getBotParameters(process)

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
    setBotParameters(botParameters, args, process)
    resetCarOnStage()
    while(True):
        winTime = process.read(pWinTime)
        if winTime > 0:
            break
        centisecondsSinceStart = process.read(pCentisecondsSinceStart)
        if(centisecondsSinceStart > 100 * 60 * 15 and centisecondsSinceStart < 0x3FFFFFFF):
            print("End2")
            return 0
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
    gamma_pan = 1.0,
    eta= 0.93,
    minimum_window=0.0
)

optimizer = BayesianOptimization(
    f=black_box_function,
    pbounds=botParametersBounds,
    random_state=random.randint(0, 0xffffffff),
    verbose=2,
    bounds_transformer=bounds_transformer,
    allow_duplicate_points=True,
)

if os.path.isfile("./logs/logsBest_202404072212_Port_Soderick.json"):
    load_logs(optimizer, logs=["./logs/logsBest_202404072212_Port_Soderick.json"])
else:
    optimizer.probe(
        params={"1": 256, "2": 255, "3": 1, "4": 5, "5": 10, "6": 50, "7": 40, "8": 25, "9": 40, "10": 250,
                "11": 250, "12": 250, "13": 250, "14": 250, "15": 250, "16": 250, "17": 250, "18": 250, "19": 250, "20": 250,
                "21": 250, "22": 100, "23": 70, "24": 60, "25": 50, "26": 50, "27": 50, "28": 50, "29": 50, "30": 50,
                "31": 40, "32": 40, "33": 40, "34": 30, "35": 70, "36": 90, "37": 60, "38": 70, "39": 40},
        lazy=True,
    )

mapName = "Port_Soderick"
logger = JSONLogger(path=f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{mapName}", reset=True)
optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)

optimizer.set_gp_params(alpha=1e-3, n_restarts_optimizer=500)
acquisition_function = UtilityFunction(kind="ucb", kappa=1e1, kappa_decay=0.80)
optimizer.maximize(
    acquisition_function=acquisition_function,
    init_points=0,
    n_iter=10000,
)