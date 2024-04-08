from LocalReadWriteMemory import ReadWriteMemory
from rallyProcess import getBotParameters


rwm = ReadWriteMemory()
process = rwm.get_process_by_name("ral.exe")
process.open()

botParameters = getBotParameters(process)


process.close()