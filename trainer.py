from LocalReadWriteMemory import ReadWriteMemory
from bayes_opt import BayesianOptimization
from bayes_opt.logger import JSONLogger
from bayes_opt.event import Events
from bayes_opt.util import load_logs
from bayes_opt import SequentialDomainReductionTransformer
import os.path
import random
from datetime import datetime
from time import sleep
from ctypes import c_uint32

def uint32(val):
    return c_uint32(val).value

random.seed(datetime.now().ctime())

def currentPlayerToPlayer0(currentPlayerAddress):
    return currentPlayerAddress - 0x719fd8 + 0x70f3ec

rwm = ReadWriteMemory()
process = rwm.get_process_by_name("ral.exe")
process.open()

def ensureWrite(ptr, value):
    value = uint32(value)
    process.write(ptr, value)
    while process.read(ptr) != value:
        print(f"value difference: { process.read(ptr):08x}{value:08x}")
        process.write(ptr, value)
        sleep(0.1)

def attemptWrites(ptrValues):
    for ptrValue in ptrValues:
        ptr = ptrValue[0]
        value = uint32(ptrValue[1])
        process.write(ptr, value)

def checkValues(ptrValues):
    for ptrValue in ptrValues:
        ptr = ptrValue[0]
        value = uint32(ptrValue[1])
        storedValue = process.read(ptr)
        if value != storedValue:
            return False
    return True

def ensureWrites(ptrValues):
    attemptWrites(ptrValues)
    while not checkValues(ptrValues):
        print("Error on writing bytes, trying again")
        attemptWrites(ptrValues)

def ensureWriteByte(ptr, value):
    process.writeByte(ptr, [value])
    while int(process.readByte(ptr)[0], base=16) != value:
        print(f"byte difference: {int(process.readByte(ptr)[0], base=16):08x}{value:08x}")
        sleep(0.1)

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
#pTriggerGameStart = process.get_pointer(currentPlayerToPlayer0(0x719FF4))
#pCurrentGearNumber = process.get_pointer(currentPlayerToPlayer0(0x71A1AC))
#pCurrentAccelerationOnPedal = process.get_pointer(currentPlayerToPlayer0(0x719FF0))

def getBotParameterBounds(botParameter):
    return (botParameter[2], botParameter[3])

def getBotParametersBounds(botParameters):
    result = {}
    for index, botParameter in enumerate(botParameters):
        result[str(index+1)] = getBotParameterBounds(botParameter)
    return result

botParameters = [
    [process.get_pointer(0x462d65), 4, 0, 256, 1], #accPedalStrength
    [process.get_pointer(0x462d59), 4, 0, 255, 1], #brakePedalStrength
    [process.get_pointer(0x462d4f), 4, 0, 1, 1], #handbrakePedalStrength
    [process.get_pointer(0x462d3d), 1, 0, 0x3f, 1], #brakeTreshold
    [process.get_pointer(0x462d44), 1, 0, 0x3f, 1], #handbrakeTreshold
    [process.get_pointer(0x462cec), 4, 0, 512, 1], #firstDesiredDoublePlaneSpeedSet
    [process.get_pointer(0x462cf3), 4, 0, 512, 1], #secondDesiredDoublePlaneSpeedSet
    [process.get_pointer(0x462cdc), 4, 0, 512, 1], #thirdDesiredDoublePlaneSpeedSet
    [process.get_pointer(0x462ce8), 1, 0, 0x3f, 1], #firstDesiredDoublePlaneSpeedCondition
    [process.get_pointer(0x71bf38), 1, 0, 0xff, 1], #botDesiredDoublePlaneSpeedByNearTurnAngleEasy
    
    [process.get_pointer(0x71bf39), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf3A), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf3B), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf3C), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf3D), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf3E), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf3F), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf40), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf41), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf42), 1, 0, 0xff, 1],
    
    [process.get_pointer(0x71bf43), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf44), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf45), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf46), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf47), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf48), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf49), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf4A), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf4B), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf4C), 1, 0, 0xff, 1],
    
    [process.get_pointer(0x71bf4D), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf4E), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf4F), 1, 0, 0xff, 1],
    [process.get_pointer(0x71bf50), 1, 0, 0xff, 1],
    [process.get_pointer(0x462ecb), 1, 0, 0x3f, 1], #firstTurnSpeedCheck
    [process.get_pointer(0x462efc), 1, 0, 0x3f, 1], #secondTurnSpeedCheck
    [process.get_pointer(0x462f2f), 1, 0, 0x3f, 1], #thirdTurnSpeedCheck
    [process.get_pointer(0x462e01), 1, 0, 0x3f, 1], #fourthTurnSpeedCheck
    [process.get_pointer(0x462e37), 1, 0, 0x3f, 1], #fifthTurnSpeedCheck
    #[process.get_pointer(0x462e98), 4, 0, 5145, 4]
]

botParametersBounds = getBotParametersBounds(botParameters)

def setBotParameters(botParameters, valuesDict):
    for index, botParameter in enumerate(botParameters):
        value = int(round(valuesDict[str(index+1)], 0))
        stepSize = botParameter[4]
        value = value * stepSize
        size = botParameter[1]
        pointer = botParameter[0]
        if size == 1:
            #previousByte = int(process.readByte(pointer)[0], base=16)
            #if(previousByte != value):
            #    print(f"Different byte {pointer:08x}: {previousByte} -> {value}")
            ensureWriteByte(pointer, value)
            #print(f"Wrote byte {pointer:08x}: {value}")
        if size == 4:
            #previousValue = process.read(pointer)
            #if(previousValue != value):
            #    print(f"Different value {pointer:08x}: {previousValue} -> {value}")
            ensureWrite(pointer, value)
            #print(f"Wrote int {pointer:08x}: {value}")

def resetCarOnStage():
    writes = []
    writes.append([pCompletedSquares, 0])
    writes.append([pWinTime, 0])
    if process.read(pCentisecondsSinceStart) > 0:
        writes.append([pCentisecondsSinceStart, -1000])
    writes.append([pCentisecondsSinceLevelLoaded, 0])
    ensureWrites(writes)
    #print("Car Reseted")

def runStage(args):
    #print(args)
    print("Start")
    setBotParameters(botParameters, args)
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
    scoreSum = 0
    scoreCount = 4
    scoreMin = 0xffffffff
    for i in range(scoreCount):
        score = runStage(args)
        if(score < scoreMin):
            scoreMin = score
        scoreSum += score
    return (scoreSum-scoreMin)/(scoreCount - 1)

def setUpGame():
    ensureWrite(pMaxWinTime, 3000000)
    ensureWrite(pMaxWinTime2, 3000000)
    ensureWrite(pFalseStartTime, 5000)
    

setUpGame()

bounds_transformer = SequentialDomainReductionTransformer(
    gamma_osc = 0.9,
    gamma_pan = 1.0,
    eta= 0.75,
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

if os.path.isfile("./logs.json"):
    load_logs(optimizer, logs=["./logs.json"])
else:
    optimizer.probe(
        params={"1": 256, "2": 255, "3": 1, "4": 5, "5": 10, "6": 50, "7": 40, "8": 25, "9": 40, "10": 250,
                "11": 250, "12": 250, "13": 250, "14": 250, "15": 250, "16": 250, "17": 250, "18": 250, "19": 250, "20": 250,
                "21": 250, "22": 100, "23": 70, "24": 60, "25": 50, "26": 50, "27": 50, "28": 50, "29": 50, "30": 50,
                "31": 40, "32": 40, "33": 40, "34": 30, "35": 70, "36": 90, "37": 60, "38": 70, "39": 40},
        lazy=True,
    )

logger = JSONLogger(path="./logs", reset=False)
optimizer.subscribe(Events.OPTIMIZATION_STEP, logger)

optimizer.set_gp_params(alpha=1e-3)#, n_restarts_optimizer=20)
optimizer.maximize(
    init_points=5,
    n_iter=10000,
)