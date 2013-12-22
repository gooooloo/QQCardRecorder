# -*- coding: cp936 -*-
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
ZP - ZhuPai (主牌)
'''

def getPid(proc_name):
	for proc in psutil.process_iter():
		try:
			if proc.name == proc_name:
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

ADD_MY_PLAYED_COUNT_LAST_ROUND = 0x004C7F30
ADD_XJ_PLAYED_COUNT_LAST_ROUND = 0x004C8278
ADD_DJ_PLAYED_COUNT_LAST_ROUND = 0x004C85C0
ADD_SJ_PLAYED_COUNT_LAST_ROUND = 0x004C8908

ADD_MY_LAST_ROUND = 0x004C7C4E
ADD_XJ_LAST_ROUND = 0x004C8626
ADD_DJ_LAST_ROUND = 0x004C82DE
ADD_SJ_LAST_ROUND = 0x004C7F96

ADD_ZP_PM = 0x004C6E20
ADD_ZP_HS = 0x004c6E38


pid = getPid(PROC_NAME)

HS = [ '', '黑', '红', '花', '方' ] # the index matches with its int value in memory
PM = [ '出错了', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '十', 'J', 'Q', 'K', '小王', '大王' ] # the index matches with its int value in memory
SXD = ['出错了', '我先出牌', '下家先出牌', '对家先出牌', '上家先出牌' ] # the index matches with its int value in memory

buffer = c_char_p(b"The data goes here")
cval = c_char()
bufferSize = len(buffer.value)
bytesRead = c_ulong(0)
def readByteAsInt(address):
	if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
		memmove(byref(cval), buffer, sizeof(cval))
		#print(hex(address), ord(cval.value))
		return ord(cval.value)
	else:
		return "Failed."

readACardAsString = lambda address : ''.join([HS[readByteAsInt(address)], PM[readByteAsInt(address + 1)]])

def captureMem():
	ret = {}
	ret['ADD_MY_LEFT_CARDS_COUNT'] = readByteAsInt(ADD_MY_LEFT_CARDS_COUNT)

	ret['ADD_MY_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_MY_PLAYED_COUNT_THIS_ROUND)
	ret['ADD_XJ_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_XJ_PLAYED_COUNT_THIS_ROUND)
	ret['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_DJ_PLAYED_COUNT_THIS_ROUND)
	ret['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] = readByteAsInt(ADD_SJ_PLAYED_COUNT_THIS_ROUND)

	ret['ADD_MY_RECENT'] = [readACardAsString(ADD_MY_RECENT + 0x8*i) for i in range(0, ret['ADD_MY_PLAYED_COUNT_THIS_ROUND'])]
	ret['ADD_XJ_RECENT'] = [readACardAsString(ADD_XJ_RECENT + 0x8*i) for i in range(0, ret['ADD_XJ_PLAYED_COUNT_THIS_ROUND'])]
	ret['ADD_DJ_RECENT'] = [readACardAsString(ADD_DJ_RECENT + 0x8*i) for i in range(0, ret['ADD_DJ_PLAYED_COUNT_THIS_ROUND'])]
	ret['ADD_SJ_RECENT'] = [readACardAsString(ADD_SJ_RECENT + 0x8*i) for i in range(0, ret['ADD_SJ_PLAYED_COUNT_THIS_ROUND'])]

	ret['ADD_MY_PLAYED_COUNT_LAST_ROUND'] = readByteAsInt(ADD_MY_PLAYED_COUNT_LAST_ROUND)
	ret['ADD_XJ_PLAYED_COUNT_LAST_ROUND'] = readByteAsInt(ADD_XJ_PLAYED_COUNT_LAST_ROUND)
	ret['ADD_DJ_PLAYED_COUNT_LAST_ROUND'] = readByteAsInt(ADD_DJ_PLAYED_COUNT_LAST_ROUND)
	ret['ADD_SJ_PLAYED_COUNT_LAST_ROUND'] = readByteAsInt(ADD_SJ_PLAYED_COUNT_LAST_ROUND)

	ret['ADD_MY_LAST_ROUND'] = [readACardAsString(ADD_MY_LAST_ROUND + 0x8*i) for i in range(0, ret['ADD_MY_PLAYED_COUNT_LAST_ROUND'])]
	ret['ADD_XJ_LAST_ROUND'] = [readACardAsString(ADD_XJ_LAST_ROUND + 0x8*i) for i in range(0, ret['ADD_XJ_PLAYED_COUNT_LAST_ROUND'])]
	ret['ADD_DJ_LAST_ROUND'] = [readACardAsString(ADD_DJ_LAST_ROUND + 0x8*i) for i in range(0, ret['ADD_DJ_PLAYED_COUNT_LAST_ROUND'])]
	ret['ADD_SJ_LAST_ROUND'] = [readACardAsString(ADD_SJ_LAST_ROUND + 0x8*i) for i in range(0, ret['ADD_SJ_PLAYED_COUNT_LAST_ROUND'])]

	return ret

roundFinished = lambda ret: ret['ADD_MY_PLAYED_COUNT_THIS_ROUND'] == 0 and ret['ADD_XJ_PLAYED_COUNT_THIS_ROUND'] == 0 and ret['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] == 0 and ret['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] == 0

def onLastPlayed(totalList, lastPlayedList, label):
	totalList.extend(lastPlayedList)
	totalList.append('|')
	for x in lastPlayedList: totalCards.remove(x)
	print(label, lastPlayedList)
	#print(label, ''.join(totalList))

def resetTotalCards():
	ret = []
	for x in PM[-2:]:
		for i in range(0, 2) :
			ret.append(x)
	for hs in HS[-4:]:
		for pm in PM[1: 14]:
			for i in range(0, 2):
				ret.append(''.join([hs,pm]))
	#printTotalCards(ret)
	assert len(ret) == 108
	return ret

def printTotalCards(totalCards):
	c = '0'
	for x in totalCards:
		if x[0] != c:
			c = x[0]
			if c != '0': print()
			print(c, end='')
		print(x[1], end='')
	print()

def hasLastRound(mem): return mem['ADD_MY_LEFT_CARDS_COUNT'] < 25
def hasNoRoundPlayed(mem): return not hasLastRound(mem)

past = {'ME':[], 'XJ':[], 'DJ':[], 'SJ':[]}
totalCards = resetTotalCards()
lastRoundHandled = False

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
while 1==1:
	sleep(0.050)
	mem = captureMem()

	assert mem['ADD_MY_PLAYED_COUNT_LAST_ROUND'] == mem['ADD_XJ_PLAYED_COUNT_LAST_ROUND']
	assert mem['ADD_MY_PLAYED_COUNT_LAST_ROUND'] == mem['ADD_DJ_PLAYED_COUNT_LAST_ROUND']
	assert mem['ADD_MY_PLAYED_COUNT_LAST_ROUND'] == mem['ADD_SJ_PLAYED_COUNT_LAST_ROUND']

	myLeftCardsCount = mem['ADD_MY_LEFT_CARDS_COUNT']

	if hasLastRound(mem):
		if roundFinished(mem):
			if not lastRoundHandled:
				onLastPlayed(past['ME'], mem['ADD_MY_LAST_ROUND'], '我家')
				onLastPlayed(past['XJ'], mem['ADD_XJ_LAST_ROUND'], '下家')
				onLastPlayed(past['DJ'], mem['ADD_DJ_LAST_ROUND'], '对家')
				onLastPlayed(past['SJ'], mem['ADD_SJ_LAST_ROUND'], '上家')
				printTotalCards(totalCards)
				print('-------')

				lastRoundHandled = True

		else: lastRoundHandled = False # we assume no another round played between 2 adjent mem-captures.
	else: # then we reset
		past = {'ME':[], 'XJ':[], 'DJ':[], 'SJ':[]}
		totalCards = resetTotalCards()
		lastRoundHandled = False


CloseHandle(processHandle)

