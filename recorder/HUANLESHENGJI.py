// this script is tent to be used for 'QQ»¶ÀÖÉý¼¶'. But not implemented yet. Yet there is another script "SHENGJI.py" doing same stuff for 'QQÉý¼¶'. If you want to implement this file for 'QQ »¶ÀÖÉý¼¶', you can refer to that script.
PROCESS_NAME == 'HLSJ.exe':
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
