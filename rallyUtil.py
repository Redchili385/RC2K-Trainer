def currentPlayerToPlayer0(currentPlayerAddress):
    return currentPlayerAddress - 0x719fd8 + 0x70f3ec

class BotParameter:
    def __init__(self, compactParameter):
        self.address = compactParameter[0]
        self.dataType = compactParameter[1]
        self.minValue = compactParameter[2]
        self.maxValue = compactParameter[3]
        self.stepSize = compactParameter[4]

def getBotInt8CompactParameter(address, min = -0x80, max = 0x7f):
    return [address, "int8", min, max, 1]

def getBotUInt8CompactParameter(address, min = 0, max = 0xFF):
    return [address, "uint8", min, max, 1]

def getBotInt32CompactParameter(address, min = -0x80000000, max = 0x7fffffff):
    return [address, "int32", min, max, 1]

def getBotTrackPolygonIndexCompactParameter(address):
    return [address, "int32", 0x9e3738, 0x9e3738 + 4 * 5145, 4]

def getBotTrackAngleIndexCompactParameter(address):
    return [address, "int32", 0x9ed800, 0x9ed800 + 4 * 5145, 4]

def getBotUInt8CompactParameters(baseAddress, count):
    return list(map(lambda i: getBotInt8CompactParameter(baseAddress + i), range(count)))

def getBotParameters():
    compactParameters = [
        getBotTrackPolygonIndexCompactParameter(0x4628a6), #AngleDetectedAhead????
        getBotInt8CompactParameter(0x4628ec), #ArePointsOutOfReachComparison
        getBotInt8CompactParameter(0x462aab, 0, 6), #tireTypeInequality
        getBotUInt8CompactParameter(0x462ad3), #firstDoublePlaneSpeedCheck
        getBotUInt8CompactParameter(0x462a16), #secondDoublePlaneSpeedCheck
        getBotTrackAngleIndexCompactParameter(0x462b31), #TrackAngleBehind1
        getBotTrackAngleIndexCompactParameter(0x462b59), #TrackAngleAhead1
        getBotInt32CompactParameter(0x462b7e, -6000, 6000), #TurnDistance1,
        getBotTrackAngleIndexCompactParameter(0x462ada), #TrackAngleBehind2
        getBotTrackAngleIndexCompactParameter(0x462b02), #TrackAngleAhead2
        getBotInt32CompactParameter(0x462b27, -6000, 6000), #TurnDistance2,
        getBotTrackAngleIndexCompactParameter(0x462a77), #TrackAngleBehind3
        getBotTrackAngleIndexCompactParameter(0x462a9f), #TrackAngleAhead3
        getBotInt32CompactParameter(0x462ac4, -6000, 6000), #TurnDistance3,
        getBotTrackAngleIndexCompactParameter(0x462a1d), #TrackAngleBehind4
        getBotTrackAngleIndexCompactParameter(0x462a4b), #TrackAngleAhead4
        getBotInt32CompactParameter(0x462a6a, 0, 127), #TurnDistance4,
        getBotTrackAngleIndexCompactParameter(0x462c1f), #NearTrackAngleAhead
        getBotUInt8CompactParameter(0x462b86), #TrackAngleDifferenceDivisionByPowerOf2
        getBotInt8CompactParameter(0x462b89), #TrackAngleDifferenceComparison
        getBotInt32CompactParameter(0x462b9f), #TrackAngleDifferenceComparison2
        getBotInt32CompactParameter(0x462bb1), #TrackAngleDifferenceComparison3
        getBotUInt8CompactParameter(0x462c75), #NearTrackAngleDifferenceDivisionByPowerOf2
        getBotInt8CompactParameter(0x462c78), #NearTrackAngleDifferenceComparison
        getBotInt8CompactParameter(0x462c7f), #NearTrackAngleDifferencePlusConstant
        getBotUInt8CompactParameter(0x462c82, 0, 24), #NearTrackAngleDifferencePlusConstantComparison
        getBotInt32CompactParameter(0x462c86, 0, 24), #NearTrackAngleDifferencePlusConstantAssignment
        getBotUInt8CompactParameter(0x462c8c), #isNextTurnHardComparisonAssignment
        getBotUInt8CompactParameter(0x462cb4), #TyreTypeTurnEasyRightComparison
        getBotInt32CompactParameter(0x462d65, 0, 256), #accPedalStrength
        getBotInt32CompactParameter(0x462d59, 0, 255), #brakePedalStrength
        getBotInt32CompactParameter(0x462d4f, 0, 1), #handbrakePedalStrength
        getBotInt8CompactParameter(0x462d3d), #brakeTreshold
        getBotInt8CompactParameter(0x462d44), #handbrakeTreshold
        getBotInt32CompactParameter(0x462cec, 0, 512), #firstDesiredDoublePlaneSpeedSet
        getBotInt32CompactParameter(0x462cf3, 0, 512), #secondDesiredDoublePlaneSpeedSet
        getBotInt32CompactParameter(0x462cdc, 0, 512), #thirdDesiredDoublePlaneSpeedSet
        getBotInt8CompactParameter(0x462ce8), #firstDesiredDoublePlaneSpeedCondition
        getBotInt8CompactParameter(0x462ecb), #firstTurnSpeedCheck
        getBotInt8CompactParameter(0x462efc), #secondTurnSpeedCheck
        getBotInt8CompactParameter(0x462f2f), #thirdTurnSpeedCheck
        getBotInt8CompactParameter(0x462e01), #fourthTurnSpeedCheck
        getBotInt8CompactParameter(0x462e37), #fifthTurnSpeedCheck
        #[process.get_pointer(0x462e98), 4, 0, 5145, 4]
    ]
    compactParameters.extend(getBotUInt8CompactParameters(0x71bf38, 25)) #botDesiredDoublePlaneSpeedByNearTurnAngleEasy
    compactParameters.extend(getBotUInt8CompactParameters(0x71bf54, 25)) #botDesiredDoublePlaneSpeedByNearTurnAngleHard
    return list(map(lambda compactParameter: BotParameter(compactParameter), compactParameters))