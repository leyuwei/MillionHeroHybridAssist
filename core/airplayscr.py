# -*- coding:utf-8 -*-

"""
    投屏软件截图支持
"""

import time
import win32gui, win32ui, win32con, win32api
import win32com.client

def get_child_windows(parent):
    if not parent:
        return
    hwndChildList = []
    win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd),  hwndChildList)
    return hwndChildList

def check_exsit():
    process_name = "airplayer.exe"
    WMI = win32com.client.GetObject('winmgmts:')
    processCodeCov = WMI.ExecQuery('select * from Win32_Process where Name="%s"' % process_name)
    if len(processCodeCov) > 0:
        return 1
    else:
        return 0

def window_capture(filename):
    main_app = "" # Airplayer
    hwnd = win32gui.FindWindow("CHWindow",main_app)
    hwnd1 = win32gui.FindWindowEx(hwnd,0,"CHWindow",None)
    if hwnd1==0:
        print("获取iOS截图失败，请确认投屏软件是否存在任务栏中，设备连接是否正常！")
    # 根据窗口句柄获取窗口的设备上下文DC（Divice Context）
    hwndDC = win32gui.GetWindowDC(hwnd1)
    # 根据窗口的DC获取mfcDC
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    # mfcDC创建可兼容的DC
    saveDC = mfcDC.CreateCompatibleDC()
    # 创建bigmap准备保存图片
    saveBitMap = win32ui.CreateBitmap()
    # 获取窗口大小
    _left,_top,_right,_bottom = win32gui.GetWindowRect(hwnd1)
    w = _right-_left
    h = _bottom-_top
    # 为bitmap开辟空间
    saveBitMap.CreateCompatibleBitmap(mfcDC, w, h)
    # 高度saveDC，将截图保存到saveBitmap中
    saveDC.SelectObject(saveBitMap)
    # 截取从左上角（0，0）长宽为（w，h）的图片
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    saveBitMap.SaveBitmapFile(saveDC, filename)