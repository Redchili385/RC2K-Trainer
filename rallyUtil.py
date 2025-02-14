def currentPlayerToPlayer0(currentPlayerAddress):
    return currentPlayerAddress - 0x719fd8 + 0x70f3ec

class BotParameter:
    def __init__(self, compactParameter):
        self.address = compactParameter[0]
        self.dataType = compactParameter[1]
        self.minValue = compactParameter[2]
        self.maxValue = compactParameter[3]
        self.stepSize = compactParameter[4]

    def __str__(self):
        return (f"BotParameter(address={self.address}, "
                f"dataType={self.dataType}, "
                f"minValue={self.minValue}, "
                f"maxValue={self.maxValue}, "
                f"stepSize={self.stepSize})")

def getBotInt8CompactParameter(address, min = -0x80, max = 0x7f):
    return [address, "int8", min, max, 1]

def getBotUInt8CompactParameter(address, min = 0, max = 0xFF):
    return [address, "uint8", min, max, 1]

def getBotInt32CompactParameter(address, min = -0x80000000, max = 0x7fffffff):
    return [address, "int32", min, max, 1]

def getBotFloat32CompactParameter(address, min = -3.4028234663852886e+38, max = 3.4028234663852886e+38):
    return [address, "float32", min, max, 1]

def getBotTrackPolygonIndexCompactParameter(address, minIndex = 0, maxIndex = 5145):
    return [address, "int32", 0x9e3738 + 4 * minIndex, 0x9e3738 + 4 * maxIndex, 4]

def getBotTrackAngleIndexCompactParameter(address, minIndex = 0, maxIndex = 5145):
    return [address, "int32", 0x9ed800 + 4 * minIndex, 0x9ed800 + 4 * maxIndex, 4]

def getBotInt8CompactParameters(baseAddress, count):
    return list(map(lambda i: getBotInt8CompactParameter(baseAddress + i), range(count)))

def getBotUInt8CompactParameters(baseAddress, count):
    return list(map(lambda i: getBotUInt8CompactParameter(baseAddress + i), range(count)))

def getBotFloat32CompactParameters(baseAddress, count, min = -3.4028234663852886e+38, max = 3.4028234663852886e+38):
    return list(map(lambda i: getBotFloat32CompactParameter(baseAddress + 4 * i, min, max), range(count)))

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
        getBotInt32CompactParameter(0x462b9f, 0, 6144), #TrackAngleDifferenceComparison2
        getBotInt32CompactParameter(0x462bb1, 0, 6144), #TrackAngleDifferenceComparison3
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
        getBotInt8CompactParameter(0x462d76, 0, 31), #minusCosTrackPositionSelector
        getBotInt32CompactParameter(0x462de2), #desiredY
        getBotInt8CompactParameter(0x462df4), #isTurnAheadVeryLargeComparison
        getBotInt8CompactParameter(0x462ec2), #isNextNearTurnHardComparison
        getBotUInt8CompactParameter(0x462ecb), #AngleDoubleSpeedComparison1
        getBotUInt8CompactParameter(0x462efc), #AngleDoubleSpeedComparison2
        getBotUInt8CompactParameter(0x462f2f), #AngleDoubleSpeedComparison3
        getBotUInt8CompactParameter(0x462e01), #AngleDoubleSpeedComparison4
        getBotUInt8CompactParameter(0x462e37), #AngleDoubleSpeedComparison5
        getBotTrackPolygonIndexCompactParameter(0x462e98, 0, 16), #AngleTrackPosition1
        getBotTrackPolygonIndexCompactParameter(0x462ed2, 0, 16), #AngleTrackPosition2
        getBotTrackPolygonIndexCompactParameter(0x462f36, 0, 16), #AngleTrackPosition3
        getBotTrackPolygonIndexCompactParameter(0x462f03, 0, 16), #AngleTrackPosition4
        getBotTrackPolygonIndexCompactParameter(0x462e6b, 0, 16), #AngleTrackPosition5
        getBotTrackPolygonIndexCompactParameter(0x462e3e, 0, 16), #AngleTrackPosition6
        getBotTrackPolygonIndexCompactParameter(0x462e08, 0, 16), #AngleTrackPosition6
        getBotInt32CompactParameter(0x462f8a), #newDesiredY
        getBotInt32CompactParameter(0x4630af), #yAttrubition?
        getBotFloat32CompactParameter(0x463130), #rotationYAttribution?
        getBotInt8CompactParameter(0x463167), #desiredRotationInversionThreshold
        getBotInt8CompactParameter(0x463182, -10, 10), #gearNumberRotationInversion
        getBotUInt8CompactParameter(0x46319b), #botCentisecondsUntilStopBrakingOrReversingComparison
        getBotInt8CompactParameter(0x4631cb), #botBrakingOrReversingGearNumberComparison
        getBotInt32CompactParameter(0x4631d4, -1, 2), #botPressGearUp
        getBotInt8CompactParameter(0x4631ac), #botBrakingOrReversingGearNumberComparison2
        getBotInt32CompactParameter(0x4631b5, -1, 2), #botPressGearDown
        getBotInt32CompactParameter(0x4631bf, 0, 256), #botBreakStrengthOnPedalWhenReversing
        getBotInt32CompactParameter(0x4631ee, 0, 1000), #CentisecondsPerReverseChecking
        getBotInt32CompactParameter(0x4631ff, -360000, 360000), #InitialCentisecondsOnReverseChecking
        getBotInt32CompactParameter(0x463270, -360000, 360000), #InternalCentisecondsOnReverseAssignment
        getBotInt32CompactParameter(0x46325e, -360000, 360000), #InternalCentisecondsOnReverseAssignment2
        getBotUInt8CompactParameter(0x46327e), #SumChangesPlus1Comparison
    ]
    compactParameters.extend(getBotUInt8CompactParameters(0x71bf38, 25)) #botDesiredDoublePlaneSpeedByNearTurnAngleEasy
    compactParameters.extend(getBotUInt8CompactParameters(0x71bf54, 25)) #botDesiredDoublePlaneSpeedByNearTurnAngleHard
    compactParameters.extend(getBotFloat32CompactParameters(0x71be9c, 32, -1.0, 1.0)) #minusCosTrackPositionMod32???
    return list(map(lambda compactParameter: BotParameter(compactParameter), compactParameters))

def setBotParameters(botParametersByKey, valuesDict, writeInt32, writeByte, writeFloat):
    for botParameter in botParametersByKey.values():
        valuesDictKey = getKeyByBotParameter(botParameter)
        if valuesDictKey not in valuesDict:
            continue
        value = valuesDict[valuesDictKey]
        dataType = botParameter.dataType
        stepSize = botParameter.stepSize
        if dataType != "float32":
            value = int(round(value, 0))
            min = botParameter.minValue
            valueDiff = value - min
            valueDiff = valueDiff - valueDiff % stepSize
            value = min + valueDiff
        address = botParameter.address
        if dataType == "uint8":
            writeByte(address, value)
        if dataType == "int8":
            writeByte(address, value)
        if dataType == "int32":
            writeInt32(address, value)
        if dataType == "float32":
            writeFloat(address, value)

def getKeyByBotParameter(botParameter):
    dataType = botParameter.dataType
    address = botParameter.address
    addressString = hex(address)
    return f"{addressString}_{dataType}"

def getBotParametersBounds(botParameters):
    result = {}
    for botParameter in botParameters:
        result[getKeyByBotParameter(botParameter)] = getBotParameterBounds(botParameter)
    return result

def getBotParameterBounds(botParameter):
    return (botParameter.minValue, botParameter.maxValue)

def getBotParametersByKey(botParameters):
    botParametersByKey = {}
    for botParameter in botParameters:
        key = getKeyByBotParameter(botParameter)
        botParametersByKey[key] = botParameter
    return botParametersByKey
