# -*- coding: cp936 -*-
from ctypes import *
from ctypes.wintypes import *
from time import sleep
import psutil
import sys

''' Vacabularies:
HS - HuaSe (花色，如黑桃，方块等等)
PM - PM (牌面，如A，2，3，J，Q，大王等等)
ZP - ZhuPai (主牌)
XS - XuanShou (选手)
SYL - ShangYiLun (上一轮)
BL - BenLun (本轮)
SXD - ShuiXianDa (谁先打)
CPS - ChuPaiShu (出牌数)
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
        ('LEFT_CARDS', XS[1], 0x004C9D1E),
        ('CPS_BL', XS[1], 0x004C8C50),
        ('CPS_BL', XS[2], 0x004C7BE8),
        ('CPS_BL', XS[3], 0x004C78A0),
        ('CPS_BL', XS[4], 0x004C7558),
        ('BL', XS[1], 0x004C896E),
        ('BL', XS[2], 0x004C7906),
        ('BL', XS[3], 0x004C75BE),
        ('BL', XS[4], 0x004C7276),
        ('CPS_SYL', XS[1], 0x004C7F30),
        ('CPS_SYL', XS[2], 0x004C8278),
        ('CPS_SYL', XS[3], 0x004C85C0),
        ('CPS_SYL', XS[4], 0x004C8908),
        ('SYL', XS[1], 0x004C7C4E),
        ('SYL', XS[2], 0x004C8626),
        ('SYL', XS[3], 0x004C82DE),
        ('SYL', XS[4], 0x004C7F96),
        ('ZP', 'PM', 0x004C6E20),
        ('ZP', 'HS', 0x004C6E38)
]

ADD_DEPENDENCY={
        'BL': 'CPS_BL',
        'SYL': 'CPS_SYL',
        'LEFT_CARDS': 'LEFT_CARDS_COUNT'
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


#################### game analysis codes block:
def makeACard(hs, pm):
        return pm if pm in [PM[14], PM[15]] else ''.join([hs,pm])

def getHsOfCard(card):
        return HS[0] if card in [PM[14], PM[15]] else card[0]

def getPmOfCard(card):
        return card if card in [PM[14], PM[15]] else card[1]

def getFenOfCard(card):
        pm = getPmOfCard(card)
        fen = {PM[5]:5, PM[10]:10, PM[13]:10}
        return fen[pm] if pm in fen else 0

def getTotalFenOfCardList(cardList):
        sum = 0
        for x in cardList:
                sum += getFenOfCard(x)
        return sum

def getPairList(cardList):
        ret = []
        if len(cardList) < 2: return ret

        #for simple, we assume the card list is in good order, and same cards are put together.
        for i in range(1, len(cardList)):
                if cardList[i] == cardList[i-1]:
                        ret.append(getHsOfCard(cardList[i]))
        return ret

def matchesPairList(pairList, pairListToMatch):
        assert len(pairListToMatch) > 0
        assert len(set(pairListToMatch)) == 1

        if len(pairList) < len(pairListToMatch): return False
        if len(set(pairList)) > 1: return False
        if pairList[0] != pairListToMatch[0]: return False;

        return True

def updateHistory(anal):
        if not 'HISTORY' in anal: anal['HISTORY'] = {}
        if not 'SXD' in anal['HISTORY']: anal['HISTORY']['SXD'] = []

        anal['HISTORY']['SXD'].append(anal['SXD'])
        anal['HISTORY']['SXD'].append('|')
        for xs in XS.values():
                if not xs in anal['HISTORY']: anal['HISTORY'][xs] = []
                anal['HISTORY'][xs].extend(anal['SYL'][xs])
                anal['HISTORY'][xs].append('|')

def updateCards(anal):
        for xs in XS.values():
                for x in anal['SYL'][xs]:
                        for y in anal['CARDS']:
                                try: anal['CARDS'][y].remove(x)
                                except: pass

def updateFen(anal):
        for xs in XS.values():
                for x in anal['SYL'][xs]:
                        if getFenOfCard(x) > 0:
                                anal['FEN'].remove(x)

def analyzeLackOfCategory(anal):
        category = analyzeCategory(anal['ZP'], anal['SYL'][anal['SXD']][0])
        for xs in XS.values():
                if xs != anal['SXD']:
                        for x in anal['SYL'][xs]:
                                if analyzeCategory(anal['ZP'], x) != category:
                                        if not category in anal['LACK_OF'][xs]['CATEGORY']:
                                                anal['LACK_OF'][xs]['CATEGORY'].append(category)

def analyzeLackOfPair(anal):
        category = analyzeCategory(anal['ZP'], anal['SYL'][anal['SXD']][0])
        pairList = getPairList(anal['SYL'][anal['SXD']])
        if len(pairList) > 0:
                for xs in XS.values():
                        if xs != anal['SXD']:
                                if not matchesPairList(getPairList(anal['SYL'][xs]), pairList):
                                        if not category in anal['LACK_OF'][xs]['PAIR_FOR_CATEGORY']:
                                                anal['LACK_OF'][xs]['PAIR_FOR_CATEGORY'].append(category)

def analyzeOnRoundFinish(anal):
        updateHistory(anal)
        updateCards(anal)
        updateFen(anal)
        analyzeLackOfCategory(anal)
        analyzeLackOfPair(anal)
        analyzePossiblePairsExceptMine(anal)

def analyzePossiblePairsExceptMine(anal):
        anal['POSSIBLE_PAIRS_EXCEPT_MINE'] = {}
        for category in anal['CARDS']:
                anal['POSSIBLE_PAIRS_EXCEPT_MINE'][category] = []
                cardList = anal['CARDS'][category]
                for i in range(1, len(cardList)):
                        if cardList[i-1] == cardList[i]:
                                if not cardList[i] in anal['MY_CARDS']:
                                        anal['POSSIBLE_PAIRS_EXCEPT_MINE'][category].append(getPmOfCard(cardList[i]))

# this is where the magic starts. All information we need from memory is these few things, and we will remember and analyze all other things!
# AMAZING, isn't it? :)
def analFromMem(anal, mem):
        assert mem['CPS_SYL'][XS[1]] == mem['CPS_SYL'][XS[2]]
        assert mem['CPS_SYL'][XS[1]] == mem['CPS_SYL'][XS[3]]
        assert mem['CPS_SYL'][XS[1]] == mem['CPS_SYL'][XS[4]]

        anal['MY_CARDS_COUNT'] = mem['LEFT_CARDS_COUNT'][XS[1]]
        anal['MY_CARDS'] = mem['LEFT_CARDS'][XS[1]]
        anal['CPS_BL'] = mem['CPS_BL']
        anal['SYL'] = mem['SYL']
        anal['ZPHS'] = mem['ZP']['HS']
        anal['ZPPM'] = mem['ZP']['PM']

        if anal['MY_CARDS_COUNT'] > anal['MAX_MY_LEFT_COUNT_IN_PAST']:
                anal['MAX_MY_LEFT_COUNT_IN_PAST'] = anal['MY_CARDS_COUNT']

        return anal

def analyzeAndUpdateXsd(anal):
        if anal['SXD'] == 'none':
                anal['SXD'] = analyzeSXD(anal)

def smartAnalyzeAndPrint(anal):
        if not isGameOngoing(anal):
                print('try to analyze but game is not ongoing')
                return anal

        if isRoundOngoing(anal):
                analyzeAndUpdateXsd(anal)
        elif anal['MY_CARDS_COUNT'] in anal['FOOTAGES']:
                pass
        else: # game ongoing but not round ongoing, then must be just finished a round, and need to update and print
                analyzeOnRoundFinish(anal)
                printAnal(anal)

                anal['SXD'] = 'none'
                anal['FOOTAGES'].append(anal['MY_CARDS_COUNT'])

        return anal

def isDeliveryingCards(anal):
        return anal['MAX_MY_LEFT_COUNT_IN_PAST'] < 25

def isRoundOngoing(anal):
        if not 'CPS_BL' in anal: # possible when we are waiting for a game
                return False

        if isDeliveryingCards(anal):
                return False

        y = [xs for xs in XS.values() if anal['CPS_BL'][xs] is not 0]
        if anal['MY_CARDS_COUNT'] >= 25:
                return len(y) > 1
        else:
                return len(y) > 0

def isGameOngoing(anal):
        if isDeliveryingCards(anal):
                return False

        myLeftCnt = anal['MY_CARDS_COUNT']
        if 0 < myLeftCnt and myLeftCnt < 25:
                return True

        if isRoundOngoing(anal):
                return True

        if myLeftCnt == 0 and len(anal['FOOTAGES']) > 0:
                return True

        return False

def analyzeSXD(anal):
        if not 'CPS_BL' in anal:
                return 'none'

        x = anal['CPS_BL']
        if (x[XS[1]] == 0):
                if (x[XS[2]]> 0): return XS[2]
                if (x[XS[3]]> 0): return XS[3]
                return XS[4]
        else:
                if (x[XS[4]]== 0): return XS[1]
                if (x[XS[3]]==0): return XS[4]
                return XS[3]


def analyzeCategory(zpcard, p):
        if getPmOfCard(p) == getPmOfCard(zpcard):
                return HS[0]
        elif getHsOfCard(p) == HS[0]:
                return HS[0]
        elif getHsOfCard(p) == getHsOfCard(zpcard):
                return HS[0]
        else:
                return getHsOfCard(p)

################### block of printing functions
def printAnal(anal):
        printMyCards(anal)
        printLeftCards(anal)
        #printHistory(anal)
        printLeftFen(anal)
        printLackOf(anal)
        printPossiblePairsExceptMine(anal)
        print('-----------------------------------------')
        print('-----------------------------------------')

def printMyCards(anal):
        print('我剩下的牌:')
        print(' '.join(anal['MY_CARDS']))
        print()

def printPossiblePairsExceptMine(anal):
        print('我之外可能的对:')
        for category in anal['POSSIBLE_PAIRS_EXCEPT_MINE']:
                print(category, end=':')
                for x in anal['POSSIBLE_PAIRS_EXCEPT_MINE'][category]:
                        print(' '+x+x, end='')
                print()
        print()

def printLeftFen(anal):
        print('剩下的分牌(', end='')
        print(getTotalFenOfCardList(anal['FEN']), end='')
        print('分):', end='')
        print(''.join(anal['FEN']))
        print()

def printLackOf(anal):
        print('推断:')
        for xs in XS.values():
                print(xs+'无', end=':')
                for y in anal['LACK_OF'][xs]['CATEGORY']:
                        print(y, end=' ')
                for y in anal['LACK_OF'][xs]['PAIR_FOR_CATEGORY']:
                        if not y in anal['LACK_OF'][xs]['CATEGORY']:
                                print(y, end='对 ')
                print()
        print()

def printHistory(anal):
        print('历史出牌纪录:')
        x = anal['HISTORY']
        print('先手:', ''.join(x['SXD']))
        for y in x:
              if y != 'SXD':
                      print(y, ''.join(x[y]))
        print()

def printLeftCards(anal):
        print('left cards:')
        for category in anal['CARDS']:
                print(category,end='')
                print('(',end='')
                print(len(anal['CARDS'][category]),end='')
                print(')',end=':')
                for card in anal['CARDS'][category]:
                        pm = getPmOfCard(card)
                        if category != HS[0]:
                                print(pm, end='')
                        elif pm in [PM[i] for i in range(1,14)] and pm != getPmOfCard(anal['ZP']):
                                print(pm, end='')
                        else:
                                print(' '+card, end='')
                print()
        print()


################### initialize
def resetAnal():
        anal = {}
        anal['FEN'] = resetFEN()
        anal['HISTORY'] = resetHistory()
        anal['MAX_MY_LEFT_COUNT_IN_PAST'] = 0
        anal['SXD'] = 'none'
        anal['FOOTAGES'] = []
        anal['LACK_OF'] = resetLackOf()
        return anal

def resetLackOf():
        ret = {}
        for xs in XS.values():
                ret[xs] = {}
                ret[xs]['CATEGORY'] = []
                ret[xs]['PAIR_FOR_CATEGORY'] = []
        return ret

def onZpReliable(anal):
        anal['ZP'] = makeACard(HS[anal['ZPHS']], PM[anal['ZPPM']])
        del anal['ZPHS']
        del anal['ZPPM']
        anal['CARDS'] = resetCards(anal['ZP'])
        return anal

def resetHistory():
        ret = {}
        ret['SXD'] = []
        for xs in XS.values():
                ret[xs] = []
        return ret

def resetFEN():
        ret = []
        for pm in [PM[5], PM[10], PM[13]]:
                for hs in HS[-4:]:
                        for x in range(2):
                                ret.append(makeACard(hs, pm))
        return ret

def resetCards(zp):
        zphs = getHsOfCard(zp)
        zppm = getPmOfCard(zp)

        assert zppm in [PM[x] for x in range(1,14)]

        ret = {}

        ret[HS[0]] = []
        for hs in HS[-4:]:
                pms = [PM[x] for x in range(2,14)]
                pms.append(PM[1])
                pms.remove(zppm)

                x = []
                for pm in pms:
                        x.append(makeACard(hs, pm))
                        x.append(makeACard(hs, pm))

                if hs == zphs:
                        ret[HS[0]].extend(x)
                else:
                        ret[hs] = x

        for hs in HS[-4:]:
                if hs != zphs:
                        ret[HS[0]].append(makeACard(hs, zppm))
                        ret[HS[0]].append(makeACard(hs, zppm))
        if zphs != HS[0]:
                ret[HS[0]].append(makeACard(zphs, zppm))
                ret[HS[0]].append(makeACard(zphs, zppm))
        ret[HS[0]].append(makeACard(zphs, PM[14]))
        ret[HS[0]].append(makeACard(zphs, PM[14]))
        ret[HS[0]].append(makeACard(zphs, PM[15]))
        ret[HS[0]].append(makeACard(zphs, PM[15]))

        return ret

##################### we start to read data from game and handle now.
if __name__ == '__main__':
        processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
        if processHandle == 0:
                print('open process failed')
        else:
                anal = resetAnal()
                while 1==1:
                        sleep(0.050)
                        mem = captureMem()

                        anal = analFromMem(anal, mem)

                        if not isGameOngoing(anal):
                                print('.', end='')
                                sys.stdout.flush()
                                if anal['MY_CARDS_COUNT'] >= 25:
                                        anal = onZpReliable(anal)
                        else:
                                anal = smartAnalyzeAndPrint(anal)

                                if anal['MY_CARDS_COUNT'] == 0:
                                        print('game finished')
                                        anal = resetAnal()

        CloseHandle(processHandle)
