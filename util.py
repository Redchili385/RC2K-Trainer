from ctypes import c_int8, c_uint8, c_int32
import json
import math

def int8(val):
    return c_int8(val).value

def uint8(val):
    return c_uint8(val).value

def int32(val):
    return c_int32(val).value

def readFile(path):
    with open(path, 'r') as file:
        return file.read()
    
def writeFile(path, content):
    with open(path, 'w') as file:
        file.write(content)
    
def parseJSON(jsonString):
    try:
        return json.loads(jsonString)
    except json.JSONDecodeError:
        print(f"Couldn't parse: {jsonString}")
        return None

def toJSON(obj):
    return json.dumps(obj)

def selectMean(meanCount, arr):
    arr.sort(reverse=True)
    sum = 0
    for i in range(meanCount):
        sum += arr[i]
    return sum/meanCount

def extendedLog2(val):
    if val <= 0:
        return float('-inf')
    return math.log2(val)
