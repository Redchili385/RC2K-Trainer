def currentPlayerToPlayer0(currentPlayerAddress):
    return currentPlayerAddress - 0x719fd8 + 0x70f3ec

class BotParameter:
    def __init__(self, compactParameter):
        self.address = compactParameter[0]
        self.size = compactParameter[1]
        self.minValue = compactParameter[2]
        self.maxValue = compactParameter[3]
        self.stepSize = compactParameter[4]

def getBotParameters():
    compactParameters = [
        [0x462d65, 4, 0, 256, 1], #accPedalStrength
        [0x462d59, 4, 0, 255, 1], #brakePedalStrength
        [0x462d4f, 4, 0, 1, 1], #handbrakePedalStrength
        [0x462d3d, 1, 0, 0x3f, 1], #brakeTreshold
        [0x462d44, 1, 0, 0x3f, 1], #handbrakeTreshold
        [0x462cec, 4, 0, 512, 1], #firstDesiredDoublePlaneSpeedSet
        [0x462cf3, 4, 0, 512, 1], #secondDesiredDoublePlaneSpeedSet
        [0x462cdc, 4, 0, 512, 1], #thirdDesiredDoublePlaneSpeedSet
        [0x462ce8, 1, 0, 0x3f, 1], #firstDesiredDoublePlaneSpeedCondition
        [0x71bf38, 1, 0, 0xff, 1], #botDesiredDoublePlaneSpeedByNearTurnAngleEasy
        
        [0x71bf39, 1, 0, 0xff, 1],
        [0x71bf3A, 1, 0, 0xff, 1],
        [0x71bf3B, 1, 0, 0xff, 1],
        [0x71bf3C, 1, 0, 0xff, 1],
        [0x71bf3D, 1, 0, 0xff, 1],
        [0x71bf3E, 1, 0, 0xff, 1],
        [0x71bf3F, 1, 0, 0xff, 1],
        [0x71bf40, 1, 0, 0xff, 1],
        [0x71bf41, 1, 0, 0xff, 1],
        [0x71bf42, 1, 0, 0xff, 1],
        
        [0x71bf43, 1, 0, 0xff, 1],
        [0x71bf44, 1, 0, 0xff, 1],
        [0x71bf45, 1, 0, 0xff, 1],
        [0x71bf46, 1, 0, 0xff, 1],
        [0x71bf47, 1, 0, 0xff, 1],
        [0x71bf48, 1, 0, 0xff, 1],
        [0x71bf49, 1, 0, 0xff, 1],
        [0x71bf4A, 1, 0, 0xff, 1],
        [0x71bf4B, 1, 0, 0xff, 1],
        [0x71bf4C, 1, 0, 0xff, 1],
        
        [0x71bf4D, 1, 0, 0xff, 1],
        [0x71bf4E, 1, 0, 0xff, 1],
        [0x71bf4F, 1, 0, 0xff, 1],
        [0x71bf50, 1, 0, 0xff, 1],
        [0x462ecb, 1, 0, 0x3f, 1], #firstTurnSpeedCheck
        [0x462efc, 1, 0, 0x3f, 1], #secondTurnSpeedCheck
        [0x462f2f, 1, 0, 0x3f, 1], #thirdTurnSpeedCheck
        [0x462e01, 1, 0, 0x3f, 1], #fourthTurnSpeedCheck
        [0x462e37, 1, 0, 0x3f, 1], #fifthTurnSpeedCheck
        #[process.get_pointer(0x462e98), 4, 0, 5145, 4]
    ]
    return list(map(lambda compactParameter: BotParameter(compactParameter), compactParameters))