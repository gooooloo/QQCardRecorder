from ctypes import *
from ctypes.wintypes import *
from time import sleep
import psutil

def getPid():
    for proc in psutil.process_iter():
        try:
            if proc.name == 'HLSJ.exe':
                return proc.pid
        except (psutil.AccessDenied) as e:
            ignoreExceptionBecauseOfPsUtilBug =("psutil.AccessDenied")

OpenProcess = windll.kernel32.OpenProcess
ReadProcessMemory = windll.kernel32.ReadProcessMemory
CloseHandle = windll.kernel32.CloseHandle

PROCESS_ALL_ACCESS = 0x1F0FFF
DIPAI_ADDRESS = 0x004AE01E
MY_CARD_ADDRESS = 0x4ae586
LastPlayedBase = 0x4abe02+0x100-4
MyLastPlayed = LastPlayedBase+0xb58
ShangJiaLastPlayed = LastPlayedBase+0xe10
DuiJiaLastPlayed = LastPlayedBase+0x10c8
XiaJiaLastPlayed = LastPlayedBase+0x1380
LAST_ROUND_CARDS_NUMBER_ADDRESS = 0x4acca8
MY_LEFT_CARD_NUMBER_ADDRESS = 0x4ae7d8


DIVIDER_LINE = "======"

pid = getPid()

buffer = c_char_p(b"The data goes here")
ival = c_int()
cval = c_char()
bufferSize = len(buffer.value)
bytesRead = c_ulong(0)

huase = {
        b'\x00':'',
        b'\x01':'黑',
        b'\x02':'红',
        b'\x03':'花',
        b'\x04':'方'
        }

dianshu = {
        b'\x00': '0',
        b'\x01': 'A',
        b'\x02': '2',
        b'\x03': '3',
        b'\x04': '4',
        b'\x05': '5',
        b'\x06': '6',
        b'\x07': '7',
        b'\x08': '8',
        b'\x09': '9',
        b'\x0a': '十',
        b'\x0b': 'J',
        b'\x0c': 'Q',
        b'\x0d': 'K',
        b'\x0e': '小王',
        b'\x0f': '大王'
        }

xianshou = {
        1:'我先出牌',
        2:'下家先出牌',
        3:'对家先出牌',
        4:'上家先出牌'
        }

def f(address, g):
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        memmove(byref(cval), buffer, sizeof(cval))
        return g[cval.value] if type(g)==dict else g(cval.value) if hasattr(g, '__call__') else cval.value
    else:
        return "Failed."

def getOneCardByAddress(add):
    return ''.join([f(add, huase),f(add+1, dianshu)])

def getCardsByAddressAndLen(pp, len):
    return ' '.join([getOneCardByAddress(pp+8*i) for i in range(0, len)])

my = []; xiajia = []; duijia = []; shangjia = [];

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)
myleftcnt = 0
while 1==1:
    sleep(0.050)
    n = f(MY_LEFT_CARD_NUMBER_ADDRESS, ord)
    if n != myleftcnt:
        myleftcnt = n
        if n == 25:
            my = []; xiajia = []; duijia = []; shangjia = [];
            print("底牌", getCardsByAddressAndLen(DIPAI_ADDRESS, 8), DIVIDER_LINE, sep='\n')
            print("我的牌", getCardsByAddressAndLen(MY_CARD_ADDRESS, 25), DIVIDER_LINE, sep='\n')
        elif n < 25:
            
            n = f(LAST_ROUND_CARDS_NUMBER_ADDRESS, ord)
            x = f(MyLastPlayed - 0x2, ord)
            
            if n >= 0 and x > 0 and x < 5:                
                my.append(getCardsByAddressAndLen(MyLastPlayed, n))
                xiajia.append(getCardsByAddressAndLen(XiaJiaLastPlayed, n))                
                duijia.append(getCardsByAddressAndLen(DuiJiaLastPlayed, n))
                shangjia.append(getCardsByAddressAndLen(ShangJiaLastPlayed, n))

                print("上一轮", xianshou[x], "出牌数", n, sep=' ')
                print("我", my)
                print("下家", xiajia)
                print("对家", duijia)
                print("上家", shangjia)
                print(DIVIDER_LINE)
                
CloseHandle(processHandle)



