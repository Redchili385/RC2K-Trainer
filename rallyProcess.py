
from processUtil import ensureWrite, ensureWriteByte

def getBotParameters(process):
    return [
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

def setBotParameters(botParameters, valuesDict, process):
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
            ensureWriteByte(pointer, value, process)
            #print(f"Wrote byte {pointer:08x}: {value}")
        if size == 4:
            #previousValue = process.read(pointer)
            #if(previousValue != value):
            #    print(f"Different value {pointer:08x}: {previousValue} -> {value}")
            ensureWrite(pointer, value, process)
            #print(f"Wrote int {pointer:08x}: {value}")

def getBotParameterBounds(botParameter):
    return (botParameter[2], botParameter[3])

def getBotParametersBounds(botParameters):
    result = {}
    for index, botParameter in enumerate(botParameters):
        result[str(index+1)] = getBotParameterBounds(botParameter)
    return result
      