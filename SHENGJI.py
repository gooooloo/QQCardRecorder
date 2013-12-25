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


######### const variant definitions
OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROC_NAME = 'NewsjRpg.exe'
PROCESS_ALL_ACCESS = 0x1F0FFF

HS = [ '主', '黑', '红', '花', '方' ] # the index matches with its int value in memory
PM = [ '出错了', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '十', 'J', 'Q', 'K', '小王', '大王' ] # the index matches with its int value in memory
SXD = ['出错了', '我先出牌', '下家先出牌', '对家先出牌', '上家先出牌' ] # the index matches with its int value in memory

ADD=[
        ('ADD_MY_LEFT_CARDS_COUNT', 0x004ca000),
        ('ADD_MY_PLAYED_COUNT_THIS_ROUND', 0x004C8C50),
        ('ADD_XJ_PLAYED_COUNT_THIS_ROUND', 0x004C7BE8),
        ('ADD_DJ_PLAYED_COUNT_THIS_ROUND', 0x004C78A0),
        ('ADD_SJ_PLAYED_COUNT_THIS_ROUND', 0x004C7558),
        ('ADD_MY_RECENT', 0x004C896E, 'ADD_MY_PLAYED_COUNT_THIS_ROUND'),
        ('ADD_XJ_RECENT', 0x004C7906, 'ADD_XJ_PLAYED_COUNT_THIS_ROUND'),
        ('ADD_DJ_RECENT', 0x004C75BE, 'ADD_DJ_PLAYED_COUNT_THIS_ROUND'),
        ('ADD_SJ_RECENT', 0x004C7276, 'ADD_SJ_PLAYED_COUNT_THIS_ROUND'),
        ('ADD_MY_PLAYED_COUNT_LAST_ROUND', 0x004C7F30),
        ('ADD_XJ_PLAYED_COUNT_LAST_ROUND', 0x004C8278),
        ('ADD_DJ_PLAYED_COUNT_LAST_ROUND', 0x004C85C0),
        ('ADD_SJ_PLAYED_COUNT_LAST_ROUND', 0x004C8908),
        ('ADD_MY_LAST_ROUND', 0x004C7C4E, 'ADD_MY_PLAYED_COUNT_LAST_ROUND'),
        ('ADD_XJ_LAST_ROUND', 0x004C8626, 'ADD_XJ_PLAYED_COUNT_LAST_ROUND'),
        ('ADD_DJ_LAST_ROUND', 0x004C82DE, 'ADD_DJ_PLAYED_COUNT_LAST_ROUND'),
        ('ADD_SJ_LAST_ROUND', 0x004C7F96, 'ADD_SJ_PLAYED_COUNT_LAST_ROUND'),
        ('ADD_ZP_PM', 0x004C6E20),
        ('ADD_ZP_HS', 0x004c6E38)
]


##################### block of memory reading codes
def getPid(proc_name):
        for proc in psutil.process_iter():
                try:
                        if proc.name == proc_name:
                                return proc.pid
                except (psutil.AccessDenied) as e:
                        ignoreExceptionBecauseOfPsUtilBug =("psutil.AccessDenied")

pid = getPid(PROC_NAME)

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

        for add in ADD:
                if len(add) == 2:
                        ret[add[0]] = readByteAsInt(add[1])
                else:
                        assert len(add) == 3
                        ret[add[0]] = [readACardAsString(add[1] + 0x8*i) for i in range(0, ret[add[2]])]

        return ret


#################### game analysis codes block:
roundFinished = lambda mem: mem['ADD_MY_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_XJ_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] == 0

def onLastPlayed(totalList, lastPlayedList, label):
        totalList.extend(lastPlayedList)
        totalList.append('|')
        for x in lastPlayedList:
                for y in totalCards:
                        try:
                                totalCards[y].remove(x)
                        except: pass
        print(label, lastPlayedList)
        #print(label, ''.join(totalList))

def hasLastRound(mem): return mem['ADD_MY_LEFT_CARDS_COUNT'] < 25

def analyzeWhoPlayedFirstThisRound(mem):
        if (mem['ADD_MY_PLAYED_COUNT_THIS_ROUND'] == 0):
                if (mem['ADD_XJ_PLAYED_COUNT_THIS_ROUND'] > 0): return 2
                if (mem['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] > 0): return 3
                return 4
        else:
                if (mem['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] == 0): return 1
                if (mem['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] == 0): return 4
                return 3
        assert False; # not supposed to be here.

def handleLastRound(mem):
        onLastPlayed(past['ME'], mem['ADD_MY_LAST_ROUND'], '我家')
        onLastPlayed(past['XJ'], mem['ADD_XJ_LAST_ROUND'], '下家')
        onLastPlayed(past['DJ'], mem['ADD_DJ_LAST_ROUND'], '对家')
        onLastPlayed(past['SJ'], mem['ADD_SJ_LAST_ROUND'], '上家')


################### block of printing functions
def printBasedOnLastRound(mem):
        print(whoPlayedFirstThisRound)
        printTotalCards(totalCards)
        print('-------')

def printTotalCards(totalCards):
        for x in totalCards:
                print(x,end=':')
                for y in totalCards[x]:
                        if x != HS[0]:
                                print(y[1], end='')
                        else:
                                print(y, end='')
                print()
        print()


################### initialize
def resetTotalCards(zphs, zppm):
        assert zphs in HS
        assert zppm in PM[1:13]

        ret = {}

        ret[HS[0]] = []
        ret[HS[0]].extend([PM[-1],PM[-1],PM[-2],PM[-2]])
        if zphs != HS[0]:
                ret[HS[0]].append(''.join([zphs, zppm]))
                ret[HS[0]].append(''.join([zphs, zppm]))
        for hs in HS[-4:]:
                if hs != zphs:
                        ret[HS[0]].append(''.join([hs, zppm]))
                        ret[HS[0]].append(''.join([hs, zppm]))

        for hs in HS[-4:]:
                y = PM[2: 14]
                y.append(PM[1])
                y.remove(zppm)

                x = []
                for pm in y:
                        x.append(''.join([hs,pm]))
                        x.append(''.join([hs,pm]))

                if hs == zphs:
                        ret[HS[0]].extend(x)
                else:
                        ret[hs] = x

        printTotalCards(ret)
        totallen = 0
        for x in ret:
                totallen += len(ret[x])
        assert totallen == 108

        return ret

past = {'ME':[], 'XJ':[], 'DJ':[], 'SJ':[]}
totalCards = {}
lastRoundHandled = False
whoPlayedFirstThisRound = 'none' # see SXD

##################### test codes
if 1==1:
        x = resetTotalCards('黑', '3')
        printTotalCards(x)



##################### we start to read data from game and handle now.
processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
while 1==1:
        sleep(0.050)
        mem = captureMem()

        assert mem['ADD_MY_PLAYED_COUNT_LAST_ROUND'] == mem['ADD_XJ_PLAYED_COUNT_LAST_ROUND']
        assert mem['ADD_MY_PLAYED_COUNT_LAST_ROUND'] == mem['ADD_DJ_PLAYED_COUNT_LAST_ROUND']
        assert mem['ADD_MY_PLAYED_COUNT_LAST_ROUND'] == mem['ADD_SJ_PLAYED_COUNT_LAST_ROUND']

        if hasLastRound(mem):
                if totalCards == {}:
                        totalCards = resetTotalCards(HS[mem['ADD_ZP_HS']], PM[mem['ADD_ZP_PM']])
                if roundFinished(mem):
                        if not lastRoundHandled:
                                handleLastRound(mem)
                                printBasedOnLastRound(mem)

                                whoPlayedFirstThisRound = 'none'
                                lastRoundHandled = True

                else:
                        lastRoundHandled = False # we assume no another round played between 2 adjent mem-captures.
                        if whoPlayedFirstThisRound == 'none':
                                whoPlayedFirstThisRound = SXD[analyzeWhoPlayedFirstThisRound(mem)]

        else: # then we reset
                past = {'ME':[], 'XJ':[], 'DJ':[], 'SJ':[]}
                totalCards = {}
                lastRoundHandled = False
                whoPlayedFirstThisRound = 'none'


CloseHandle(processHandle)

