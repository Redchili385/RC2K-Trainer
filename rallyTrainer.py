from datetime import datetime
import json
from math import sqrt
from rallyProcess import RallyProcess
from rallyUtil import getBotParameters, getBotParametersBounds, getBotParametersByKey
from util import parseJSON, readFile, selectMean

class RallyTrainer:
  def __init__(self, process: RallyProcess, initBotParameterValuesWithTargetList: "list[dict]" = None):
    self.process = process
    self.numberOfRunsPerEvaluation = 1
    self.mapName = "Arcade_2"
    self.fileToLogPath = f"./logs/logs_{datetime.now().strftime('%Y%m%d%H%M')}_{self.mapName}.json"
    self.setUpGame()
    self.setInitialProperties()
    self.setInitialTrainingProperties()
    self.initBotParameterValuesList = [
      self.process.getBotParameterValuesByKey(self.trainingBotParameterByKey),
    ]
    if initBotParameterValuesWithTargetList is not None:
      self.setBestParameters(initBotParameterValuesWithTargetList)
      # for initBotParameterValuesWithTarget in initBotParameterValuesWithTargetList:
      #   botParameterValues = {k: initBotParameterValuesWithTarget["params"][k] for k in initBotParameterValuesWithTarget["params"] if k in self.botParameterByKey}
      #   self.initBotParameterValuesList.append(botParameterValues)

  def setUpGame(self):
    self.process.holdCarOnStage()
    self.process.holdEnter()
    self.process.speedUpTime(1000)

  def setInitialProperties(self):
    self.botParameters = getBotParameters()
    self.botParameterByKey = getBotParametersByKey(self.botParameters)
    self.botParametersBounds = getBotParametersBounds(self.botParameters)

  def setInitialTrainingProperties(self):
    priority = 3
    trainingBotParameterIndexes = self.getBotParameterIndexesByTrainingPriorityGroup()[priority]
    trainingBotParameterIndexesSet = set(trainingBotParameterIndexes)
    self.trainingBotParameters = list(filter(lambda botParameter: botParameter.address in trainingBotParameterIndexesSet, self.botParameters))
    self.trainingBotParameterByKey = getBotParametersByKey(self.trainingBotParameters)
    self.trainingBotParametersBounds = getBotParametersBounds(self.trainingBotParameters)

  def setBestParameters(self, botParameterValuesWithTargetList):
    bestParamsWithTarget = {}
    for botParameterValuesWithTarget in botParameterValuesWithTargetList:
      target = botParameterValuesWithTarget["target"]
      params = botParameterValuesWithTarget["params"]
      for key in params:
        value = params[key]
        if key not in bestParamsWithTarget or bestParamsWithTarget[key]["bestTarget"] < target:
          bestParamsWithTarget[key] = {"bestTarget": target, "value": value}
    bestParams = {}
    for key in bestParamsWithTarget:
      bestParams[key] = bestParamsWithTarget[key]["value"]
    self.process.setBotParameterValues(self.botParameterByKey, bestParams)

  def black_box_function(self, **args):
    scores = []
    for i in range(self.numberOfRunsPerEvaluation):
        time = self.process.runArcade(self.botParameterByKey, args)
        speed = 100/time  # L/s   (L = Total Length in meters)
        scale = 10**8
        scaleSpeed = sqrt(scale)
        score = pow(speed * scaleSpeed, 2) # J * L /kg - Specific Kinectic Energy   
        scores.append(score) 
    return selectMean(1, scores)
  
  @staticmethod
  def getBotParameterIndexesByTrainingPriorityGroup():
    return [
      [0x462ad3, 0x462a16, 0x462b31, 0x462b59, 0x462ada, 0x462b02, 0x462a77, 0x462a9f, 0x462a1d, 0x462a4b, 0x462c1f, 0x462b9f, 0x462bb1, 0x462c78, 0x462c7f, 0x462c82, 0x462c86, 0x462d65, 0x462d59, 0x462d4f, 0x462d3d, 0x462d44, 0x462cec, 0x462cf3, 0x462cdc, 0x462ce8, 0x462d76],
      [0x71bf38 + i * 1 for i in range(25)],
      [0x71bf54 + i * 1 for i in range(25)],
      [0x71be9c + i * 4 for i in range(32)],
      [0x4628a6, 0x4628ec, 0x462aab, 0x462b7e, 0x462b27, 0x462ac4, 0x462a6a, 0x462b86, 0x462b89, 0x462c75, 0x462c8c, 0x462cb4, 0x462de2, 0x462df4, 0x462ec2, 0x462f8a, 0x4630af, 0x463130, 0x463167, 0x463182, 0x46319b, 0x4631cb, 0x4631d4, 0x4631ac, 0x4631b5, 0x4631bf, 0x4631ff, 0x463270, 0x46325e, 0x46327e],
    ]
    