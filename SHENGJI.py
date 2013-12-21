from ctypes import *
from ctypes.wintypes import *
from time import sleep
import psutil

''' Vacabularies:
XJ - XiaJia (下家)
DJ - DuiJia (对家)
SJ - ShangJia (上家)
HS - HuaSe (花色，如黑桃，方块等等)
PM - PM (牌面，如A，2，3，J，Q，大王等等)
SXD - ShuiXianDa (该轮谁先打的，我还是下家还是对家上家)
'''

def getPid(proc_name):
	for proc in psutil.process_iter():
		try:
			if proc.name == proc_name
				return proc.pid
		except (psutil.AccessDenied) as e:
			ignoreExceptionBecauseOfPsUtilBug =("psutil.AccessDenied")

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROC_NAME = 'NewsjRpg.exe'
PROCESS_ALL_ACCESS = 0x1F0FFF

ADD_MY_LEFT_CARDS_COUNT = 0x004ca000
ADD_MY_RECENT = 0x004C896E
ADD_MY_PLAYED_COUNT_THIS_ROUND = 0x004C8C50
ADD_XJ_RECENT = 0x004C7906
ADD_XJ_PLAYED_COUNT_THIS_ROUND = 0x004C7BE8
ADD_DJ_RECENT = 0x004C75BE
ADD_DJ_PLAYED_COUNT_THIS_ROUND = 0x004C78A0
ADD_SJ_RECENT = 0x004C7276
ADD_SJ_PLAYED_COUNT_THIS_ROUND = 0x004C7558


pid = getPid(PROC_NAME)

HS = [ '', '黑', '红', '花', '方' ] # the index matches with its int value in memory
PM = [ '出错了', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '十', 'J', 'Q', 'K', '小王', '大王' ] # the index matches with its int value in memory
SXD = ['出错了', '我先出牌', '下家先出牌', '对家先出牌', '上家先出牌' ] # the index matches with its int value in memory

def readByteAsInt(address):
	buffer = c_char_p(b"The data goes here")
	cval = c_char()
	bufferSize = len(buffer.value)
	bytesRead = c_ulong(0)
	if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
		memmove(byref(cval), buffer, sizeof(cval))
		return ord(cval.value)
	else:
		return "Failed."

readACardAsString = lambda address : ''.join([HS[readByteAsInt(address)], PM[readByteAsInt(address + 1)]])

def captureMem():
	ret = {}
	ret['ADD_MY_LEFT_CARDS_COUNT'] = readByteAsInt(ADD_MY_LEFT_CARDS_COUNT)
	red['ADD_MY_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_MY_PLAYED_COUNT_THIS_ROUND)
	red['ADD_XJ_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_XJ_PLAYED_COUNT_THIS_ROUND)
	red['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_DJ_PLAYED_COUNT_THIS_ROUND)
	red['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_SJ_PLAYED_COUNT_THIS_ROUND)

	ret['ADD_MY_RECENT'] = [readACardAsString(ADD_MY_RECENT + 0x8*i) for i in range(0, ret['ADD_MY_PLAYED_COUNT_THIS_ROUND'])]
	ret['ADD_XJ_RECENT'] = [readACardAsString(ADD_XJ_RECENT + 0x8*i) for i in range(0, ret['ADD_XJ_PLAYED_COUNT_THIS_ROUND'])]
	ret['ADD_DJ_RECENT'] = [readACardAsString(ADD_DJ_RECENT + 0x8*i) for i in range(0, ret['ADD_DJ_PLAYED_COUNT_THIS_ROUND'])]
	ret['ADD_SJ_RECENT'] = [readACardAsString(ADD_SJ_RECENT + 0x8*i) for i in range(0, ret['ADD_SJ_PLAYED_COUNT_THIS_ROUND'])]
	return ret

#TODO: continue below contents.
processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
past = {'me':[], 'XiaJia':[], 'DuiJia':[], 'ShangJia':[]}
mem = captureMem()
while 1==1:
	sleep(0.050)
	memOld = mem
	mem = captureMem()

	if mem['myCardsCnt'] == 25:
		past = {'me':[], 'XiaJia':[], 'DuiJia':[], 'ShangJia':[]}
		#print(mem['diPaiCards'])

	elif mem['myCardsCnt'] < memOld['myCardsCnt']: # means I played a card out
		past['me'].append((mem['lr_me']))
		past['XiaJia'].append((mem['lr_XiaJia']))
		past['DuiJia'].append((mem['lr_DuiJia']))
		past['ShangJia'].append((mem['lr_ShangJia']))

		print('1 round')
		if mem['myCardsCnt'] == 0: print(past)



CloseHandle(processHandle)



