import json

class RallyTrainingResultsService:

  @staticmethod
  def loadBestBotParameterValuesList(path):
    with open(path, 'r') as file:
      content = file.read()
      bestRunRecord = json.loads(content)
      return bestRunRecord["bestBotParameterValues"]
