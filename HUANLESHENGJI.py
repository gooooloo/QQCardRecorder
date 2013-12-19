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
ADD_DIPAI = 0x004AE01E
ADD_MY_CARDS = 0x4ae586
ADD_MY_CARDS_NUMBER = 0x4ae7d8
ADD_LAST_BASE = 0x4abe02+0x100-4
ADD_LAST_ME = ADD_LAST_BASE+0xb58
ADD_LAST_SHANG_JIA = ADD_LAST_BASE+0xe10
ADD_LAST_DUI_JIA = ADD_LAST_BASE+0x10c8
ADD_LAST_XIA_JIA = ADD_LAST_BASE+0x1380
ADD_LAST_CARDS_NUMBER = 0x4acca8

DIVIDER_LINE = "======"

pid = getPid()

huase = [ '', '黑', '红', '花', '方' ]
dianshu = [ '0', 'A', '2', '3', '4', '5', '6', '7', '8', '9', '十', 'J', 'Q', 'K', '小王', '大王' ]
xianshou = ['出错了', '我先出牌', '下家先出牌', '对家先出牌', '上家先出牌' ]

def f(address):
	buffer = c_char_p(b"The data goes here")
	cval = c_char()
	bufferSize = len(buffer.value)
	bytesRead = c_ulong(0)
	if ReadProcessMemory(processHandle, address, buffer, bufferSize, byref(bytesRead)):
		memmove(byref(cval), buffer, sizeof(cval))
		return ord(cval.value)
	else:
		return "Failed."

g = lambda x : ''.join([huase[f(x)], dianshu[f(x+1)]])
h = lambda x : ''.join([xianshou[f(x-2)], g(x)])

def captureMem():
	ret = {}
	ret['myCardsCnt'] = f(ADD_MY_CARDS_NUMBER)
	ret['mycards'] = [g(ADD_MY_CARDS + 0x8*i) for i in range(0, ret['myCardsCnt'])]
	ret['diPaiCards'] = [g(ADD_DIPAI + 0x8*i) for i in range(0, 8)]
	ret['lr_cnt'] = f(ADD_LAST_CARDS_NUMBER)
	ret['lr_me'] = [h(ADD_LAST_ME + 0x8*i) for i in range(0, ret['lr_cnt'])]
	ret['lr_XiaJia'] = [h(ADD_LAST_XIA_JIA + 0x8*i) for i in range(0, ret['lr_cnt'])]
	ret['lr_DuiJia'] = [h(ADD_LAST_DUI_JIA + 0x8*i) for i in range(0, ret['lr_cnt'])]
	ret['lr_ShangJia'] = [h(ADD_LAST_SHANG_JIA + 0x8*i) for i in range(0, ret['lr_cnt'])]
	return ret

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



