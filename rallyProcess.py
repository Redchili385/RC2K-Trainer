
from time import sleep
from process import Process
from rallyUtil import currentPlayerToPlayer0, getKeyByBotParameter, setBotParameters

class RallyProcess(Process):
    def __init__(self, processName = "ral_botTraining_220424.exe"):
        super().__init__(processName)
        self.setBasicAddresses()

    def setBasicAddresses(self):
        self.pWinTime = currentPlayerToPlayer0(0x71A080) #timeStppedCarToWin
        self.pGameOverFlag = currentPlayerToPlayer0(0x71A088)
        self.pCompletedSquares = currentPlayerToPlayer0(0x71A068)
        self.pCentisecondsSinceStart = currentPlayerToPlayer0(0x71A060)
        self.pCentisecondsSinceLevelLoaded = currentPlayerToPlayer0(0x719FEC)
        self.pArcadeStageIndex = 0x7587f0
        self.pMaxWinTime = 0x436a13
        self.pMaxWinTime2 = 0x436a39
        self.pFalseStartTime = 0x43b9f4
        self.pValidTrackPosition = 0x70f3ec+0x94
        self.pMaximumTrackPosition = 0x623640
        self.pEngineDamageAddress = 0x70f3ec+0*0xfe0+0x2B8
        self.pArcadeModeInnerMode = 0x487f3f

    def resetCarOnStage(self):
        addrValues = []
        addrValues.append([self.pCompletedSquares, 0])
        addrValues.append([self.pWinTime, 0])
        if self.rwmProcess.read(self.pCentisecondsSinceStart) > 0:
            addrValues.append([self.pCentisecondsSinceStart, -1000])
        addrValues.append([self.pCentisecondsSinceLevelLoaded, 0])
        self.freezeGameLoop()
        self.ensureWriteInt32Values(addrValues)
        self.unfreezeGameLoop()

    def runStage(self, botParametersByKey, args):
        #print(args)
        print("Start")
        self.setBotParameterValues(botParametersByKey, args)
        self.resetCarOnStage()
        return self.waitForStageResults()
    
    def waitForStageResults(self):
        result = None
        while(result is None):
            result = self.getStageResults()
            sleep(0.1)
        return result
    
    def waitForStageStart(self):
        while(self.readInt32(self.pWinTime) != 0):
            sleep(0.1)
    
    def getStageResults(self):
        winTime = self.readInt32(self.pWinTime)
        centisecondsSinceStart = self.readInt32(self.pCentisecondsSinceStart)
        if winTime > 0:
            centisecondsSinceStart = self.readInt32(self.pCentisecondsSinceStart)
            print("End")
            return centisecondsSinceStart, True
        maximumTrainingSessionTime = 100 * 60 * 15
        if(centisecondsSinceStart > maximumTrainingSessionTime and centisecondsSinceStart < 0x3FFFFFFF):
            print("End2")
            validTrackPosition = self.readInt32(self.pValidTrackPosition)
            maximumTrackPosition = self.readInt32(self.pMaximumTrackPosition)
            engineDamage = self.readFloat(self.pEngineDamageAddress)
            return (maximumTrainingSessionTime) * (maximumTrackPosition/ validTrackPosition) / (1 - engineDamage), False
        return None
    
    def runArcade(self, botParametersByKey, args, stageTries = 3, stageRepeatTimes = 2):
        self.setBotParameterValues(botParametersByKey, args)
        self.ensureWriteByte(self.pArcadeModeInnerMode, 0x00)
        sumArcadeTime = 0
        for arcadeStageIndex in range(6):
            print("Arcade Stage Index: ", arcadeStageIndex + 1)
            minTime = 0x3FFFFFFF
            for repeatIndex in range(stageRepeatTimes):
                for j in range(stageTries):
                    print("Repeat: ", repeatIndex + 1, "Try: ", j + 1)
                    stageResults = self.waitForStageResults()
                    completed = stageResults[1]
                    print("Time: ", stageResults[0])
                    print("Completed: ", completed)
                    minTime = min(minTime, stageResults[0])
                    if((not completed) and (j < stageTries - 1)):
                        self.resetCarOnStage()
                        continue
                    break
                if(repeatIndex < stageRepeatTimes - 1):
                    self.resetCarOnStage()
                    continue
                while(self.getCurrentArcadeStageIndex() == arcadeStageIndex + 1):
                    self.ensureWin()
                    self.goToNextStage()
                    self.waitForStageStart()
                break
            sumArcadeTime += minTime
        return sumArcadeTime

    def getBotParameterValuesByKey(self, botParameterByKey):
        valuesDict = {}
        for botParameter in botParameterByKey.values():
            valuesDictKey = getKeyByBotParameter(botParameter)
            dataType = botParameter.dataType
            address = botParameter.address
            if dataType == "uint8":
                value = self.readByte(address)
            if dataType == "int8":
                value = self.readByte(address)
                if value > 127:
                    value = value - 256
            if dataType == "int32":
                value = self.readInt32(address)
                if value > 0x7fffffff:
                    value = value - 0x100000000
            if dataType == "float32":
                value = self.readFloat(address)
            valuesDict[valuesDictKey] = value
        return valuesDict

    def setBotParameterValues(self, botParametersByKey, valuesDict):
        def writeInt32(address, value):
            self.ensureWriteInt32(address, value)
        def writeByte(address, value):
            self.ensureWriteByte(address, value)
        def writeFloat(address, value):
            self.ensureWriteFloat(address, value)
        self.freezeGameLoop()
        setBotParameters(botParametersByKey, valuesDict, writeInt32, writeByte, writeFloat)
        self.unfreezeGameLoop()

    def holdEnter(self):
        self.freezeGameLoop()
        self.ensureWriteByte(0x466031, 0x90)
        self.ensureWriteByte(0x466032, 0x90)
        self.ensureWriteInt32(0x465fff, 0x90909090)
        self.ensureWriteByte(0x466003, 0x90)
        self.ensureWriteByte(0x466004, 0x90)
        self.unfreezeGameLoop()

    def releaseEnter(self):
        self.freezeGameLoop()
        self.ensureWriteByte(0x466031, 0x75)
        self.ensureWriteByte(0x466032, 0x3E)
        self.ensureWriteInt32(0x465fff, 0x0128840f)
        self.ensureWriteByte(0x466003, 0x00)
        self.ensureWriteByte(0x466004, 0x0)
        self.unfreezeGameLoop()

    def holdCarOnStage(self):
        self.freezeGameLoop()
        self.ensureWriteInt32(self.pMaxWinTime, 3000000)
        self.ensureWriteInt32(self.pMaxWinTime2, 3000000)
        self.ensureWriteInt32(self.pFalseStartTime, 5000)
        self.unfreezeGameLoop()

    def releaseCarOnStage(self):
        self.freezeGameLoop()
        self.ensureWriteInt32(self.pMaxWinTime, 0)
        self.ensureWriteInt32(self.pMaxWinTime2, 0)
        self.ensureWriteInt32(self.pFalseStartTime, 0)
        self.unfreezeGameLoop()

    def ensureWin(self):
        self.freezeGameLoop()
        self.ensureWriteInt32(self.pGameOverFlag, 2)
        self.ensureWriteInt32(self.pWinTime, 30000)
        self.unfreezeGameLoop()

    def goToNextStage(self):
        self.releaseCarOnStage()
        sleep(0.5)
        self.holdCarOnStage()

    def getCurrentArcadeStageIndex(self):
        return self.readInt32(self.pArcadeStageIndex)
    
    def freezeGameLoop(self):
        self.ensureWriteByte(0x4454fb, 0x00)
        sleep(0.01)
    
    def unfreezeGameLoop(self):
        self.ensureWriteByte(0x4454fb, 0xEF)
