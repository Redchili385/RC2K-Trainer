from ctypes import c_uint32
import json

def uint32(val):
    return c_uint32(val).value

def readFile(path):
    with open(path, 'r') as file:
        return file.read()
    
def parseJSON(jsonString):
    try:
        return json.loads(jsonString)
    except json.JSONDecodeError:
        print(f"Couldn't parse: {jsonString}")
        return None

def selectMean(meanCount, arr):
    arr.sort(reverse=True)
    sum = 0
    for i in range(meanCount):
        sum += arr[i]
    return sum/meanCount