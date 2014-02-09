# -*- coding: cp936 -*-
from ctypes import *
from ctypes.wintypes import *
from time import sleep
import psutil
import SHENGJI.py

utarray = []

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

def testResetHistory():
        ret = resetHistory()
        assert len(ret) == 4
utarray.append(resetHistory)

def testConvertToFEN():
        assert convertToFEN('方5') == 5
        assert convertToFEN('方十') == 10
        assert convertToFEN('方K') == 10
        assert convertToFEN('方Q') == 0
utarray.append(testConvertToFEN)

def testResetREN():
        ret = resetFEN()
        assert len(ret) == 24
        assert 200 == sum([convertToFEN(x) for x in ret])
utarray.append(testResetREN)

def testMakeACard():
        assert makeACard('方', '3') == '方3'
        assert makeACard('主', '大王') == '大王'
        assert makeACard('主', '小王') == '小王'
        assert makeACard('主', '3') == '主3'
utarray.append(testMakeACard)

def testGetHs():
        assert getHsOfCard("大王") == "主"
        assert getHsOfCard("小王") == "主"
        assert getHsOfCard("方3") == "方"
        assert getHsOfCard("主3") == "主"
utarray.append(testGetHs)

def testGetPm():
        assert getPmOfCard("大王") == "大王"
        assert getPmOfCard("小王") == "小王"
        assert getPmOfCard("方J") == "J"
utarray.append(testGetPm)

def testHasPair():
        assert getPairList(['大王','大王']) == ['主']
        assert getPairList(['大王','大王', '红3', '红3']) == ['主', '红']
        assert getPairList(['方4', '大王','大王']) == ['主']
        assert getPairList(['大王']) == []
        assert getPairList(['小王','大王']) == []
utarray.append(testHasPair)

def testMatchPairList():
        assert matchesPairList(['主'], ['主'])
        assert not matchesPairList(['方'], ['主'])
        assert not matchesPairList(['方'], ['方', '方'])
utarray.append(testMatchPairList)

def testAnalSylCategory():
        anal = resetAnal('黑', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['黑3']
        anal['SYL']['下家'] = ['红4']
        anal['SYL']['对家'] = ['梅5']
        anal['SYL']['上家'] = ['方6']

        analOnceRoundFinished(anal)

        assert anal['sylCategory'] == '红'
utarray.append(testAnalSylCategory)
def testLackOfColorBasic():
        anal = resetAnal('黑', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['黑3']
        anal['SYL']['下家'] = ['红4']
        anal['SYL']['对家'] = ['梅5']
        anal['SYL']['上家'] = ['方6']

        analOnceRoundFinished(anal)

        assert '本家无红' in anal['conclusions']
        assert '对家无红' in anal['conclusions']
        assert '上家无红' in anal['conclusions']
utarray.append(testLackOfColorBasic)
def testLackOfColorComplex():
        anal = resetAnal('黑', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['黑3', '红3']
        anal['SYL']['下家'] = ['红4', '红5']
        anal['SYL']['对家'] = ['梅5', '红5']
        anal['SYL']['上家'] = ['方6', '红6']

        analOnceRoundFinished(anal)

        assert '本家无红' in anal['conclusions']
        assert '对家无红' in anal['conclusions']
        assert '上家无红' in anal['conclusions']
utarray.append(testLackOfColorComplex)
def testLackOfZP():
        anal = resetAnal('红', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['黑3']
        anal['SYL']['下家'] = ['红4']
        anal['SYL']['对家'] = ['梅5']
        anal['SYL']['上家'] = ['方6']

        analOnceRoundFinished(anal)

        assert '本家无主' in anal['conclusions']
        assert '对家无主' in anal['conclusions']
        assert '上家无主' in anal['conclusions']
utarray.append(testLackOfZP)
def testLackOfZP2():
        anal = resetAnal('红', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['黑3']
        anal['SYL']['下家'] = ['大王']
        anal['SYL']['对家'] = ['梅5']
        anal['SYL']['上家'] = ['方6']

        analOnceRoundFinished(anal)

        assert '本家无主' in anal['conclusions']
        assert '对家无主' in anal['conclusions']
        assert '上家无主' in anal['conclusions']
utarray.append(testLackOfZP2)
def testLackOfPair():
        anal = resetAnal('黑', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['红8', '红3']
        anal['SYL']['下家'] = ['红4', '红4']
        anal['SYL']['对家'] = ['红9', '红5']
        anal['SYL']['上家'] = ['红J', '红6']

        analOnceRoundFinished(anal)
        assert '本家无红对' in anal['conclusions']
        assert '对家无红对' in anal['conclusions']
        assert '上家无红对' in anal['conclusions']
utarray.append(testLackOfPair)
def testLackOfPairComplex():
        anal = resetAnal('黑', '2')
        anal['SYL_SXD'] = '下家'
        anal['SYL'] = {}
        anal['SYL']['本家'] = ['红8', '红3']
        anal['SYL']['下家'] = ['红4', '红4']
        anal['SYL']['对家'] = ['黑5', '黑5']
        anal['SYL']['上家'] = ['红J', '红6']

        analOnceRoundFinished(anal)
        assert '本家无红对' in anal['conclusions']
        assert '对家无红对' in anal['conclusions']
        assert '上家无红对' in anal['conclusions']
utarray.append(testLackOfPairComplex)

def testAnalSxd():
        mem = {}
        mem['CPS_BL'] = {}
        def f(x,y): mem['CPS_BL'][XS[x]]=y
        def g(y1,y2,y3,y4):
                f(1,y1)
                f(2,y2)
                f(3,y3)
                f(4,y4)
        g(0,0,0,1)
        assert analSxd(mem) == '上家'
        g(0,0,1,1)
        assert analSxd(mem) == '对家'
        g(0,1,1,1)
        assert analSxd(mem) == '下家'
        g(1,0,0,0)
        assert analSxd(mem) == '本家'
        g(1,0,0,1)
        assert analSxd(mem) == '上家'
        g(1,0,1,1)
        assert analSxd(mem) == '对家'
utarray.append(testAnalSxd)

def testGetCatogory():
        anal = {}
        anal['zp'] = '黑2'
        assert getCatogoryFromTotalCards(anal, '红2') == '主'
        assert getCatogoryFromTotalCards(anal, '黑2') == '主'
        assert getCatogoryFromTotalCards(anal, '黑3') == '主'
        assert getCatogoryFromTotalCards(anal, '大王') == '主'
        assert getCatogoryFromTotalCards(anal, '小王') == '主'
        assert getCatogoryFromTotalCards(anal, '红3') == '红'
        anal['zp'] = '主2'
        assert getCatogoryFromTotalCards(anal, '红2') == '主'
        assert getCatogoryFromTotalCards(anal, '黑3') == '黑'
        assert getCatogoryFromTotalCards(anal, '大王') == '主'
        assert getCatogoryFromTotalCards(anal, '小王') == '主'
utarray.append(testGetCatogory)


testing = 1==0
if testing:
        for ut in utarray:
                ut()
        print('ut passed')

