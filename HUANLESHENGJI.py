from ctypes import *
from ctypes.wintypes import *
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
MyLastPlayed = LastPlayedBase+0x78
ShangJiaLastPlayed = LastPlayedBase+0x330
DuiJiaLastPlayed = LastPlayedBase+0x5e8
XiaJiaLastPlayed = LastPlayedBase+0x8a0

DIVIDER_LINE = "======"

pid = getPid()

buffer = c_char_p(b"The data goes here")
ival = c_int()
cval = c_char()
bufferSize = len(buffer.value)
bytesRead = c_ulong(0)

processHandle = OpenProcess(PROCESS_ALL_ACCESS, False, pid)

'''
def printHuanLeDou():
    print("欢乐豆")
    address = 0x#TODO
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        memmove(byref(ival), buffer, sizeof(ival))
        print("Success:" + str(ival.value))
    else:
        print("Failed.")
'''

huase = {
        b'\x00':'无',
        b'\x01':'  黑',
        b'\x02':'    红',
        b'\x03':'      花',
        b'\x04':'        方'
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

def f(address, g):
    if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
        memmove(byref(cval), buffer, sizeof(cval))
        return g[cval.value]
    else:
        return "Failed."

def getCardsByAddressAndLen(pp, len):
    return '\n'.join(['   '.join([f(pp+8*i, huase),f(pp+8*i+1, dianshu)]) for i in range(0, len)])

print("底牌", getCardsByAddressAndLen(DIPAI_ADDRESS, 8), DIVIDER_LINE, sep='\n')
print("我的牌", getCardsByAddressAndLen(MY_CARD_ADDRESS, 25+8), DIVIDER_LINE, sep='\n')
print("上一轮我出牌", getCardsByAddressAndLen(MyLastPlayed, 5), sep='\n')
print("上一轮下家出牌", getCardsByAddressAndLen(XiaJiaLastPlayed, 5), sep='\n')
print("上一轮对家出牌", getCardsByAddressAndLen(DuiJiaLastPlayed, 5), sep='\n')
print("上一轮上家出牌", getCardsByAddressAndLen(ShangJiaLastPlayed, 5), sep='\n')



CloseHandle(processHandle)

