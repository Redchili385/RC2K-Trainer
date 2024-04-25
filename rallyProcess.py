
from time import sleep
from process import Process
from rallyUtil import currentPlayerToPlayer0, getBotParameters, getKeyByBotParameter, setBotParameters
from util import parseJSON, readFile

class RallyProcess(Process):
    def __init__(self, processName = "ral_botTraining_220424.exe"):
        super().__init__(processName)
        self.setBasicAddresses()

    def setBasicAddresses(self):
        self.pWinTime = currentPlayerToPlayer0(0x71A080) #timeStppedCarToWin
        self.pCompletedSquares = currentPlayerToPlayer0(0x71A068)
        self.pCentisecondsSinceStart = currentPlayerToPlayer0(0x71A060)
        self.pCentisecondsSinceLevelLoaded = currentPlayerToPlayer0(0x719FEC)
        self.pMaxWinTime = 0x436a13
        self.pMaxWinTime2 = 0x436a39
        self.pFalseStartTime = 0x43b9f4
        self.pValidTrackPosition = 0x70f3ec+0x94
        self.pMaximumTrackPosition = 0x623640
        self.pEngineDamageAddress = 0x70f3ec+0*0xfe0+0x2B8

    def resetCarOnStage(self):
        addrValues = []
        addrValues.append([self.pCompletedSquares, 0])
        addrValues.append([self.pWinTime, 0])
        if self.rwmProcess.read(self.pCentisecondsSinceStart) > 0:
            addrValues.append([self.pCentisecondsSinceStart, -1000])
        addrValues.append([self.pCentisecondsSinceLevelLoaded, 0])
        self.ensureWriteInt32Values(addrValues)

    def runStage(self, botParametersByKey, args):
        #print(args)
        print("Start")
        self.setBotParameterValues(botParametersByKey, args)
        self.resetCarOnStage()
        while(True):
            winTime = self.readInt32(self.pWinTime)
            if winTime > 0:
                break
            centisecondsSinceStart = self.readInt32(self.pCentisecondsSinceStart)
            maximumTrainingSessionTime = 100 * 60 * 15
            if(centisecondsSinceStart > maximumTrainingSessionTime and centisecondsSinceStart < 0x3FFFFFFF):
                print("End2")
                validTrackPosition = self.readInt32(self.pValidTrackPosition)
                maximumTrackPosition = self.readInt32(self.pMaximumTrackPosition)
                engineDamage = self.readFloat(self.pEngineDamageAddress)
                return (6000/maximumTrainingSessionTime) * (validTrackPosition / maximumTrackPosition) * (1 - engineDamage)
            sleep(0.1)
        time = self.readInt32(self.pCentisecondsSinceStart)
        #print(time)
        print("End")
        return 6000/time

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
        setBotParameters(botParametersByKey, valuesDict, writeInt32, writeByte, writeFloat)

    def setBestParameters(self, jsonParametersPath = "./logs/logs_202404240509_Port_Soderick.json", lineIndex = 75):
        logsBestString = readFile(jsonParametersPath)
        logsBestStrings = logsBestString.split("\n")
        logsBestList = [parseJSON(line) for line in logsBestStrings if parseJSON(line) is not None]
        bestLog = logsBestList[lineIndex]
        self.setBotParameterValues(getBotParameters(), bestLog["params"])
      