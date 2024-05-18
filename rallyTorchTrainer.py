import json
import torch
from rallyTrainer import RallyTrainer
from rallyUtil import getKeyByBotParameter

class RallyTorchTrainer(RallyTrainer):
  def __init__(self, process):
    super().__init__(process)
    self.base_tensor, _ = self.getInitialInputValuesTorch()
    self.setBoundProperties()
    

  def setBoundProperties(self):
    self.initialBounds = self.botParameterBoundsToTensor(self.botParametersBounds)
    print("initialBounds")
    print(self.initialBounds)
    print("initialBoundsSize")
    print(self.initialBounds.shape[1])
    self.initialInputValuesTorch, _ = self.getInitialInputValuesTorch()
    print("initialInputValuesTorch")
    print(self.initialInputValuesTorch)
    boundsWindow = 0.005
    unitBoundsAmplitude = 1.5
    self.unitBounds = torch.cat((torch.zeros(self.initialBounds.shape[1]).unsqueeze(0), torch.ones(self.initialBounds.shape[1]).unsqueeze(0))).transpose(0, 1) * unitBoundsAmplitude - unitBoundsAmplitude/2
    print(self.unitBounds)
    print(self.initialInputValuesTorch.unsqueeze(1))
    print("sum")
    print(self.initialInputValuesTorch.unsqueeze(1) + self.unitBounds)
    self.bounds = torch.clamp(self.initialInputValuesTorch.unsqueeze(1) + self.unitBounds, min=self.initialBounds[0].unsqueeze(1), max=self.initialBounds[1].unsqueeze(1))
    #bounds = initialInputValuesTorch.unsqueeze(1) + unitBounds
    #bounds = (initialBounds - initialInputValuesTorch)*boundsWindow + initialInputValuesTorch
    print("bounds")
    print(self.bounds)
    self.transposedBounds = self.bounds.clone().detach().transpose(0, 1)
    print("transposedBounds")
    print(self.transposedBounds)
    self.initialInputValuesTorch = torch.clamp(self.initialInputValuesTorch, min=self.transposedBounds[0], max=self.transposedBounds[1])
    print("clampedInitialInputValuesTorch")
    print(self.initialInputValuesTorch)

  def botParameterBoundsToTensor(botParameterBounds):
    tensorBounds = []
    for botParameterBound in botParameterBounds.values():
        min = float(botParameterBound[0])
        max = float(botParameterBound[1])
        tensorBounds.append([min, max])
    return torch.tensor(tensorBounds, dtype=torch.float32).transpose(0, 1)
  
  def tensorToBotParameterValuesByKey(self, tensor: torch.Tensor, botParameters):
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
  
  def botParameterValuesByKeyToTensor(self, botParameterValuesByKey, botParameters):
    tensor = []
    for botParameter in botParameters:
        key = getKeyByBotParameter(botParameter)
        tensor.append(botParameterValuesByKey[key])
    return torch.tensor(tensor, dtype=torch.float32)
  
  def logStepValue(self, stepParams, target: torch.Tensor):
    file = open(self.fileToLogPath, "a")
    botParameterValues = self.tensorToBotParameterValuesByKey(stepParams)
    file.write(json.dumps({
        "target": target.item(),
        "params": botParameterValues
    }))
    file.write("\n")
    file.close()
  
  def black_box_torch_function(self, input_tensor: torch.Tensor):
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
        copied_base_tensor = self.base_tensor.clone().detach()
        copied_base_tensor[:input_tensor_size] = input_tensor_line[:input_tensor_size]
        # print("copied_base_tensor")
        # print(copied_base_tensor)
        botParameterValuesByKey = self.tensorToBotParameterValuesByKey(copied_base_tensor)
        target = self.black_box_function(**botParameterValuesByKey)
        targetTensor = torch.tensor([target], dtype=torch.float32)
        self.logStepValue(input_tensor_line, targetTensor)
        # print("sumTarget")
        # print(sumTarget)
        # print(targetTensor)
        sumTarget = torch.cat((sumTarget, targetTensor), dim=0)
    return sumTarget
  
  def getInitialInputValuesTorch(self):
    botParameterValuesByKey = self.process.getBotParameterValuesByKey(self.botParameterByKey)
    return self.botParameterValuesByKeyToTensor(botParameterValuesByKey, self.botParameters), botParameterValuesByKey
  
  def getInitialValueTorch(self):
    botParameterValuesTensor, botParameterValuesByKey = self.getInitialInputValuesTorch()
    print("botParameterValuesTensor")
    print(botParameterValuesTensor)
    targetTensor = torch.tensor([self.black_box_function(**botParameterValuesByKey)], dtype=torch.float32)
    return botParameterValuesTensor, targetTensor
  
  def getInitialValuesTorch(self, bounds: torch.Tensor):
    torchInitialValues, torchTarget = self.getInitialValueTorch()
    torchInitialValues = torchInitialValues.unsqueeze(0)
    torchTarget = torchTarget.unsqueeze(0)
    for bound in bounds:
        boundTarget = self.black_box_torch_function(bound)
        torchTarget = torch.cat((torchTarget, boundTarget.unsqueeze(0)), dim=0)
        torchInitialValues = torch.cat((torchInitialValues, bound.unsqueeze(0)), dim=0)
    return torchInitialValues, torchTarget