# -*- coding: cp936 -*-
from ctypes import *
from ctypes.wintypes import *
from time import sleep
import psutil

''' Vacabularies:
HS - HuaSe (花色，如黑桃，方块等等)
PM - PM (牌面，如A，2，3，J，Q，大王等等)
ZP - ZhuPai (主牌)
XS - XuanShou (选手)
SYL - ShangYiLun (上一轮)
SXD - ShuiXianDa (谁先打)
'''


######### const variant definitions
OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROC_NAME = 'NewsjRpg.exe'
PROCESS_ALL_ACCESS = 0x1F0FFF

HS = [ '主', '黑', '红', '梅', '方' ] # the index matches with its int value in memory
PM = { 1:'A', 2:'2', 3:'3', 4:'4', 5:'5', 6:'6', 7:'7', 8:'8', 9:'9', 10:'十', 11:'J', 12:'Q', 13:'K', 14:'小王', 15:'大王' }
XS = {1:'本家', 2:'下家', 3:'对家', 4:'上家' }

ADD=[
        ('LEFT_CARDS_COUNT', XS[1], 0x004ca000),
        ('PLAYED_COUNT_THIS_ROUND', XS[1], 0x004C8C50),
        ('PLAYED_COUNT_THIS_ROUND', XS[2], 0x004C7BE8),
        ('PLAYED_COUNT_THIS_ROUND', XS[3], 0x004C78A0),
        ('PLAYED_COUNT_THIS_ROUND', XS[4], 0x004C7558),
        ('RECENT', XS[1], 0x004C896E),
        ('RECENT', XS[2], 0x004C7906),
        ('RECENT', XS[3], 0x004C75BE),
        ('RECENT', XS[4], 0x004C7276),
        ('PLAYED_COUNT_SYL', XS[1], 0x004C7F30),
        ('PLAYED_COUNT_SYL', XS[2], 0x004C8278),
        ('PLAYED_COUNT_SYL', XS[3], 0x004C85C0),
        ('PLAYED_COUNT_SYL', XS[4], 0x004C8908),
        ('SYL', XS[1], 0x004C7C4E),
        ('SYL', XS[2], 0x004C8626),
        ('SYL', XS[3], 0x004C82DE),
        ('SYL', XS[4], 0x004C7F96),
        ('ZP', 'PM', 0x004C6E20),
        ('ZP', 'HS', 0x004c6E38)
]

ADD_DEPENDENCY={
        'RECENT', 'PLAYED_COUNT_THIS_ROUND',
        'SYL', 'PLAYED_COUNT_SYL'
}


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
                assert len(add) == 3
                if add[0] not in ADD_DEPENDENCY:
                        ret[add[0]] = {}
                        ret[add[0]][add[1]] = readByteAsInt(add[2])
        for add in ADD:
                if add[0] in ADD_DEPENDENCY:
                        ret[add[0]][add[1]] = [readACardAsString(add[2] + 0x8*i) for i in range(0, ret[ADD_DEPENDENCY[add[0]]][add[1]])]

        return ret


#################### game analysis codes block:

anal = {}

def resetAnal():
        anal = {}
        anal['cards'] = resetTotalCards()
        anal['backupCards'] = resetTotalCards()

def analFromMen():
        anal['roundFinished'] = analRoundFinished()
        anal['hasLastRound'] = (mem['LEFT_CARDS_COUNT'][XS[1]] < 25)
        anal['sylSxd'] = analSxd()
        for xs in XS:
                anal['history'][xs].extend(mem['SYL'][xs])
                anal['history'][xs].append('|')
        anal['lastRoundCatogory'] = getCatogoryFromTotalCards(mem['SYL'][analSxd()])
        for xs in XS:
                for x in mem['SYL'][xs]:
                        for y in anal['cards']:
                                try: anal['cards'].remove(x)
                                except: pass

def analRoundFinished():
        return (mem['PLAYED_COUNT_THIS_ROUND', XS[1]] == 0 and mem['XJ_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] == 0)

def analSxd():
        if (mem['PLAYED_COUNT_THIS_ROUND', XS[1]] == 0):
                if (mem['XJ_PLAYED_COUNT_THIS_ROUND'] > 0): return 2
                if (mem['DJ_PLAYED_COUNT_THIS_ROUND'] > 0): return 3
                return 4
        else:
                if (mem['SJ_PLAYED_COUNT_THIS_ROUND'] == 0): return 1
                if (mem['DJ_PLAYED_COUNT_THIS_ROUND'] == 0): return 4
                return 3
        assert False; # not supposed to be here.

def getCatogoryFromTotalCards(p):
        for x in anal['backupCards']:
                if p in anal['backupCards'][x]:
                        return x

################### block of printing functions
def printBasedOnLastRound(mem, zppm):
        print(whoPlayedFirstThisRound)
        printTotalCards(totalCards, zppm)
        print('-------')

def printTotalCards(totalCards, zppm):
        for x in totalCards:
                print(x,end=':')
                for y in totalCards[x]:
                        if x != HS[0]:
                                print(y[1], end='')
                        elif y[1] in PM[1:14] and y[1] != zppm:
                                print(y[1], end='')
                        else:
                                print(' '+y, end='')
                print()
        print()


################### initialize
def resetTotalCards(zphs, zppm):
        assert zphs in HS
        assert zppm in PM[1:13]

        ret = {}

        ret[HS[0]] = []
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

        for hs in HS[-4:]:
                if hs != zphs:
                        ret[HS[0]].append(''.join([hs, zppm]))
                        ret[HS[0]].append(''.join([hs, zppm]))
        if zphs != HS[0]:
                ret[HS[0]].append(''.join([zphs, zppm]))
                ret[HS[0]].append(''.join([zphs, zppm]))
        ret[HS[0]].extend([PM[-2],PM[-2],PM[-1],PM[-1]])
        
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
testing = 1==1
if testing:
        x = resetTotalCards('主', 'A')
        printTotalCards(x, 'A')
        assert getCatogoryFromTotalCards(x, '大王') == '主'
        assert getCatogoryFromTotalCards(x, '方A') == '主'
        assert getCatogoryFromTotalCards(x, '方K') == '方'
        x = resetTotalCards('方', 'A')
        printTotalCards(x, 'A')
        assert getCatogoryFromTotalCards(x, '大王') == '主'
        assert getCatogoryFromTotalCards(x, '方A') == '主'
        assert getCatogoryFromTotalCards(x, '红A') == '主'
        assert getCatogoryFromTotalCards(x, '方K') == '主'
        assert getCatogoryFromTotalCards(x, '黑K') == '黑'


##################### we start to read data from game and handle now.
processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
while 1==1 and not testing:
        sleep(0.050)
        mem = captureMem()

        assert mem['PLAYED_COUNT_SYL', XS[1]] == mem['XJ_PLAYED_COUNT_SYL']
        assert mem['PLAYED_COUNT_SYL', XS[1]] == mem['DJ_PLAYED_COUNT_SYL']
        assert mem['PLAYED_COUNT_SYL', XS[1]] == mem['SJ_PLAYED_COUNT_SYL']

        if hasLastRound(mem):
                if totalCards == {}:
                        totalCards = resetTotalCards(HS[mem['ZP_HS']], PM[mem['ADD_ZP_PM']])
                if roundFinished(mem):
                        if not lastRoundHandled:
                                handleLastRound(mem)
                                printBasedOnLastRound(mem, PM[mem['ZP_PM']])

                                whoPlayedFirstThisRound = 'none'
                                lastRoundHandled = True

                else:
                        lastRoundHandled = False # we assume no another round played between 2 adjent mem-captures.
                        if whoPlayedFirstThisRound == 'none':
                                whoPlayedFirstThisRound = SXD[analSxd(mem)]

        else: # then we reset
                past = {'ME':[], 'XJ':[], 'DJ':[], 'SJ':[]}
                totalCards = {}
                lastRoundHandled = False
                whoPlayedFirstThisRound = 'none'


CloseHandle(processHandle)

