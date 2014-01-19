# -*- coding: cp936 -*-
import time

##################### save / load
def getFileNameForSave():
        timestamp = time.strftime('%y.%m.%d.%H.%M',time.localtime(time.time()))
        return 'game.recored.'+timestamp+'.txt'

def saveGame(anal):
        name = getFileNameForSave()
        saveGameHistory(anal['HISTORY'], name)
        return name

def friendHistory(history):
        for x in history:
                y = history[x]
                history[x] = ''.join(y)
        return history

def saveGameHistory(history, name):
        try:
                with open(name, 'w') as out:
                        printGameHistoryToFile(friendHistory(history), out)
        except IOError as err:
                print('failed to save file' + str(err))

def printGameHistoryToFile(friendlyHistory, outFile):
        attrs = ['SXD', '本家', '下家', '对家', '上家']
        for x in attrs:
                print(x+':'+friendlyHistory[x], file=outFile)

def uploadFile(name):
        pass # TODO

##################### we start to read data from game and handle now.
if __name__ == '__main__':
        history = {'下家': ['方Q', '方4', '方3', '方3', '|', '黑6', '|', '梅6', '梅6', '|', '梅9', '梅4', '|', '红4', '红4', '|', '梅A', '梅5', '|', '方2', '|', '黑4', '黑4', '|', '黑十', '|', '红6', '|', '梅2', '|', '红5', '|', '红J', '红7', '红7', '|'], 'SXD': ['本家', '|', '本家', '|', '本家', '|', '本家', '|', '本家', '|', '本家', '|', '本家', '|', '对家', '|', '对家', '|', '本家', '|', '上家', '|', '下家', '|', '本家', '|'], '上家': ['方A', '方K', '方J', '方5', '|', '黑3', '|', '梅J', '梅9', '|', '梅十', '黑J', '|', '红3', '红3', '|', '黑Q', '黑5', '|', '红6', '|', '黑A', '黑十', '|', '红K', '|', '红2', '|', '红8', '|', '梅2', '|', '黑2', '红Q', '红9', '|'], '本家': ['方8', '方8', '方7', '方7', '|', '黑A', '|', '梅Q', '梅Q', '|', '梅7', '梅7', '|', '红A', '红A', '|', '梅3', '梅3', '|', '红8', '|', '黑K', '黑Q', '|', '方2', '|', '红5', '|', '红J', '|', '红2', '|', '梅K', '梅J', '梅5', '|'], '对家': ['方9', '方9', '方6', '方6', '|', '黑6', '|', '梅8', '梅8', '|', '梅K', '梅十', '|', '红十', '红9', '|', '梅A', '梅4', '|', '小王', '|', '黑9', '黑9', '|', '黑7', '|', '黑2', '|', '红Q', '|', '方十', '|', '方A', '黑J', '黑8', '|']}
        
        saveGameHistory(history, 'test.~')
