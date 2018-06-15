from PIL import ImageGrab
import time, os
import win32gui, win32ui, win32con, win32api
import cv2 as cv

captureFileName = "test.bmp"
targetWidth = 1080
template = cv.imread("icon2.bmp", 0)
tw, th = template.shape[::-1]


def findWindow():
    parent = win32gui.FindWindow("LDPlayerMainFrame", "雷电模拟器")
    hwndChildList = []
    win32gui.EnumChildWindows(parent, lambda hwnd, param: param.append(hwnd), hwndChildList)
    return hwndChildList[1]


def capture(hwnd, name=captureFileName):
    left, top, right, bottom = win32gui.GetWindowRect(hwnd)
    w = right - left
    h = bottom - top

    hwndDC = win32gui.GetWindowDC(hwnd)
    mfcDC = win32ui.CreateDCFromHandle(hwndDC)
    saveDC = mfcDC.CreateCompatibleDC()
    bitmap = win32ui.CreateBitmap()
    bitmap.CreateCompatibleBitmap(mfcDC, w, h)
    saveDC.SelectObject(bitmap)
    saveDC.BitBlt((0, 0), (w, h), mfcDC, (0, 0), win32con.SRCCOPY)
    bitmap.SaveBitmapFile(saveDC, name)
    return (w, h)


def findLocation(img, template, ratio, drawResult=False):
    img_rgb = cv.imread(img, 0)
    res = cv.matchTemplate(img_rgb, template, cv.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv.minMaxLoc(res)

    if max_val < 0.7:
        return None

    if drawResult:
        rgb = cv.imread(img)
        cv.rectangle(rgb, max_loc, (max_loc[0] + tw, max_loc[1] + th), (0, 0, 255), 3)
        cv.imwrite("res.png", rgb)

    return int(max_loc[0] * ratio), int(max_loc[1] * ratio)


def sendTap(x, y):
    os.system("adb shell input tap %d %d" % (x, y))

start = time.time()

hwnd = findWindow()
sw, sh = capture(hwnd)
print("capture img w =", sw, "h =", sh)
ratio = targetWidth / sw
print("ratio=", ratio)
result = findLocation(captureFileName, template, ratio, False)
if result is not None:
    x, y = result
    print(result)
    sendTap(x, y)
else:
    print("未找到匹配项")

end = time.time()

print("use time :", end - start)


def testSpeed():
    beg = time.time()
    for i in range(10):
        capture(hwnd, "capture%s" % i)
    end = time.time()
    print(end - beg)
