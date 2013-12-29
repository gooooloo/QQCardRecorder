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

######### test method array
utarray = []

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
        'RECENT': 'PLAYED_COUNT_THIS_ROUND',
        'SYL': 'PLAYED_COUNT_SYL'
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
                key0 = add[0]
                key1 = add[1]
                hexadd = add[2]
                if key0 not in ADD_DEPENDENCY:
                        if not key0 in ret:
                                ret[key0] = {}
                        ret[key0][key1] = readByteAsInt(hexadd)
        for add in ADD:
                assert len(add) == 3
                key0 = add[0]
                key1 = add[1]
                hexadd = add[2]
                if key0 in ADD_DEPENDENCY:
                        keydep0 = ADD_DEPENDENCY[key0]
                        if not key0 in ret:
                                ret[key0] = {}
                        ret[key0][key1] = [readACardAsString(hexadd + 0x8*i) for i in range(0, ret[keydep0][key1])]

        return ret

def testCaptureMem():
        global readByteAsInt
        global readACardAsString
        readByteAsIntBackUP = readByteAsInt
        readACardAsStringBackUP = readACardAsString

        readByteAsInt = lambda x : 3
        readACardAsString = lambda x : '黑2'

        captureMem()

        readACardAsString = readACardAsStringBackUP
        readByteAsInt = readByteAsIntBackUP

utarray.append(testCaptureMem)
#################### game analysis codes block:


def resetAnal(zphs, zppm):
        anal = {}
        anal['cards'] = resetCards(zphs, zppm)
        anal['backupCards'] = resetCards(zphs, zppm)
        anal['conclusions'] = []
        anal['FEN'] = resetFEN()
        anal['history'] = resetHistory()
        return anal

def resetHistory():
        ret = {}
        for xs in XS.values():
                ret[xs] = []
        return ret
def testResetHistory():
        ret = resetHistory()
        assert len(ret) == 4
utarray.append(resetHistory)

def convertToFEN(card):
        assert len(card) in [2,3]
        pm = card[1]
        fen = {PM[5]:5, PM[10]:10, PM[13]:10}
        return fen[pm] if pm in fen else 0
def testConvertToFEN():
        assert convertToFEN('方5') == 5
        assert convertToFEN('方十') == 10
        assert convertToFEN('方K') == 10
        assert convertToFEN('方Q') == 0
utarray.append(testConvertToFEN)

def resetFEN():
        ret = []
        for pm in [PM[5], PM[10], PM[13]]:
                for hs in HS[-4:]:
                        for x in range(2):
                                ret.append(''.join([hs, pm]))
        return ret
def testResetREN():
        ret = resetFEN()
        assert len(ret) == 24
        assert 200 == sum([convertToFEN(x) for x in ret])
utarray.append(testResetREN)

def makeACard(hs, pm):
        return ''.join([hs,pm])
def testMakeACard():
        assert makeACard('方', '3') == '方3'
        assert makeACard('主', '大王') == '主大王'
        assert makeACard('主', '小王') == '主小王'
utarray.append(testMakeACard)

def analOnceRoundFinished(anal, mem):
        for xs in XS.values():
                anal['history'][xs].extend(mem['SYL'][xs])
                anal['history'][xs].append('|')
                for x in mem['SYL'][xs]:
                        for y in anal['cards']:
                                try: anal['cards'].remove(x)
                                except: pass
                        if convertToFEN(x) > 0:
                                anal['FEN'].remove(x)
        anal['sylCategory'] = getCatogoryFromTotalCards(mem['SYL'][anal['sylSxd']][0])
        for xs in XS.values():
                if xs != anal['sylSxd']:
                        for x in mem['SYL'][xs]:
                                if getCatogoryFromTotalCards(x) != anal['sylCategory']:
                                        anal['conclusions'].append(xs+'无'+anal['sylCategory'])
        del anal['sylSxd']
def testAnalOnceRoundFinished():
        anal = resetAnal('黑', '2')
        anal['sylSxd'] = '下家'
        mem = {}
        mem['SYL'] = {}
        mem['SYL']['本家'] = ['黑3']
        mem['SYL']['下家'] = ['红4']
        mem['SYL']['对家'] = ['梅5']
        mem['SYL']['上家'] = ['方6']

        analOnceRoundFinished(anal, mem)

        assert anal['sylCategory'] == '红'
utarray.append(testAnalOnceRoundFinished)


def analFromMem():
        anal['roundFinished'] = analRoundFinished()
        anal['hasLastRound'] = (mem['LEFT_CARDS_COUNT'][XS[1]] < 25)
        anal['zp'] = makeACard(mem['ZP']['HS'], mem['ZP']['PM'])
        if anal['roundFinished']:
                analOnceRoundFinished()
        else:
                if not 'sylSxd' in anal:
                        anal['sylSxd'] = analSxd()

def analRoundFinished():
        return (mem['PLAYED_COUNT_THIS_ROUND', XS[1]] == 0 and mem['XJ_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_DJ_PLAYED_COUNT_THIS_ROUND'] == 0 and mem['ADD_SJ_PLAYED_COUNT_THIS_ROUND'] == 0)

def analSxd(mem):
        tmp = mem['PLAYED_COUNT_THIS_ROUND']
        if (tmp[XS[1]] == 0):
                if (tmp[XS[2]]> 0): return XS[2]
                if (tmp[XS[3]]> 0): return XS[3]
                return XS[4]
        else:
                if (tmp[XS[4]]== 0): return XS[1]
                if (tmp[XS[3]]==0): return XS[4]
                return XS[3]
def testAnalSxd():
        mem = {}
        mem['PLAYED_COUNT_THIS_ROUND'] = {}
        def f(x,y): mem['PLAYED_COUNT_THIS_ROUND'][XS[x]]=y
        def g(y1,y2,y3,y4):
                f(1,y1)
                f(2,y2)
                f(3,y3)
                f(4,y4)
        g(0,0,0,1)
        assert analSxd() == '上家'
        g(0,0,1,1)
        assert analSxd() == '对家'
        g(0,1,1,1)
        assert analSxd() == '下家'
        g(1,0,0,0)
        assert analSxd() == '本家'
        g(1,0,0,1)
        assert analSxd() == '上家'
        g(1,0,1,1)
        assert analSxd() == '对家'
utarray.append(testAnalSxd)


def getCatogoryFromTotalCards(p):
        for x in anal['backupCards']:
                if p in anal['backupCards'][x]:
                        return x

################### block of printing functions
def printAnal():
        printLeftCards()
        print('-------')

def printLeftCards():
        for x in anal['cards']:
                print(x,end=':')
                for y in anal['cards'][x]:
                        if x != HS[0]:
                                print(y[1], end='')
                        elif y[1] in PM[1:14] and y[1] != anal['zppm']:
                                print(y[1], end='')
                        else:
                                print(' '+y, end='')
                print()
        print()


################### initialize
def resetCards(zphs, zppm):
        assert zphs in HS
        assert zppm in [PM[x] for x in range(1,14)]

        ret = {}

        ret[HS[0]] = []
        for hs in HS[-4:]:
                y = [PM[x] for x in range(2,14)]
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
        ret[HS[0]].extend([PM[14],PM[14],PM[15],PM[15]])

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
        for ut in utarray:
                ut()
        print('ut passed')
        '''
        x = resetCards('主', 'A')
        printTotalCards(x, 'A')
        assert getCatogoryFromTotalCards(x, '大王') == '主'
        assert getCatogoryFromTotalCards(x, '方A') == '主'
        assert getCatogoryFromTotalCards(x, '方K') == '方'
        x = resetCards('方', 'A')
        printTotalCards(x, 'A')
        assert getCatogoryFromTotalCards(x, '大王') == '主'
        assert getCatogoryFromTotalCards(x, '方A') == '主'
        assert getCatogoryFromTotalCards(x, '红A') == '主'
        assert getCatogoryFromTotalCards(x, '方K') == '主'
        assert getCatogoryFromTotalCards(x, '黑K') == '黑'
'''

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
                        totalCards = resetCards(HS[mem['ZP_HS']], PM[mem['ADD_ZP_PM']])
                if roundFinished(mem):
                        if not lastRoundHandled:
                                handleLastRound(mem)
                                printAnal(mem, PM[mem['ZP_PM']])

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

