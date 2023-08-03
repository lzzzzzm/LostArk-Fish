import argparse
import time
import cv2
import keyboard
import mss
import numpy as np
import win32com.client
import win32con
import win32gui
import pyautogui

from find_template import find_fish

class ScreenCapture:
    """
    parameters
    ----------
        screen_frame : Tuple[int, int]
            屏幕宽高，分别为x，y
        region : Tuple[float, float]
            实际截图范围，分别为x，y，(1.0, 1.0)表示全屏检测，越低检测范围越小(始终保持屏幕中心为中心)
        window_name : str
            显示窗口名
        exit_key : int
            结束窗口的退出键值，为键盘各键对应的ASCII码值，默认是ESC键
    """

    def __init__(self, screen_frame=(1920, 1080), region=(0.5, 0.5), window_name='test', exit_key=0x1B, template='img/template.png', score=0.7):
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--region', type=tuple, default=region,
                                 help='截图范围；分别为x，y，(1.0, 1.0)表示全屏检测，越低检测范围越小(始终保持屏幕中心为中心)')
        self.parser_args = self.parser.parse_args()

        self.cap = mss.mss()  # 实例化mss，并使用高效模式

        self.screen_width = screen_frame[0]  # 屏幕的宽
        self.screen_height = screen_frame[1]  # 屏幕的高
        self.mouse_x, self.mouse_y = self.screen_width // 2, self.screen_height // 2  # 屏幕中心点坐标

        # 截图区域
        self.GAME_WIDTH, self.GAME_HEIGHT = int(self.screen_width * self.parser_args.region[0]), int(
            self.screen_height * self.parser_args.region[1])  # 宽高
        self.GAME_LEFT, self.GAME_TOP = int(0 + self.screen_width // 2 * (1. - self.parser_args.region[0])), int(
            0 + 1080 // 2 * (1. - self.parser_args.region[1]))  # 原点

        self.RESZIE_WIN_WIDTH, self.RESIZE_WIN_HEIGHT = self.screen_width // 4, self.screen_height // 4  # 显示窗口大小
        self.mointor = {
            'left': self.GAME_LEFT,
            'top': self.GAME_TOP,
            'width': self.GAME_WIDTH,
            'height': self.GAME_HEIGHT
        }
        self.template = cv2.imread(template)

        self.window_name = window_name
        self.Exit_key = exit_key
        self.img = None
        self.count = 0
        self.score = score

    def grab_screen_mss(self, monitor):
        # cap.grab截取图片，np.array将图片转为数组，cvtColor将BRGA转为BRG,去掉了透明通道
        return cv2.cvtColor(np.array(self.cap.grab(monitor)), cv2.COLOR_BGRA2BGR)

    def update_img(self, img):
        self.img = img

    def get_img(self):
        return self.img

    def run(self):
        ready = False
        SetForegroundWindow_f = 0  # 判断是否需要置顶窗口
        fish_ready = False
        t1_state = False
        while True:
            run_time = time.time()
            if fish_ready:
                pyautogui.press('e')
                fish_ready = False

            # 判断是否按下 ctrl+U 窗口始终置顶
            if keyboard.is_pressed('ctrl+U'):
                while keyboard.is_pressed('ctrl+U'):
                    continue
                if SetForegroundWindow_f == 0:
                    SetForegroundWindow_f = 1
                    time.sleep(1)
                    continue
                else:
                    SetForegroundWindow_f = 0

            if self.img is None:
                img = self.grab_screen_mss(self.mointor)

            img, capture = find_fish(self.template, img, self.score)
            # if not capture and not t1_state:
            #     t1_state = True
            #     t1 = time.time()
            #
            # if not capture and t1_state:
            #     t2 = time.time()
            #     if t2 - t1 > 50:
            #         fish_ready = True
            #         t1_state = False

            # cap发现后，一定时间后再继续
            if capture:
                ready = True
                up_time = time.time()
                time.sleep(0.5)
                pyautogui.press('e')
            if ready:
                down_time = time.time()
                # 5s之后
                if down_time - up_time > 10:
                    down_time = 0
                    up_time = 0
                    fish_ready = True
                    ready = False

            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)  # cv2.WINDOW_NORMAL 根据窗口大小设置图片大小
            cv2.resizeWindow(self.window_name, self.RESZIE_WIN_WIDTH, self.RESIZE_WIN_HEIGHT)
            cv2.imshow(self.window_name, img)

            if SetForegroundWindow_f == 1:
                shell = win32com.client.Dispatch("WScript.Shell")
                shell.SendKeys('%')
                win32gui.SetForegroundWindow(win32gui.FindWindow(None, self.window_name))
                win32gui.ShowWindow(win32gui.FindWindow(None, self.window_name), win32con.SW_SHOW)

            if cv2.waitKey(1) & 0XFF == self.Exit_key:  # 默认：ESC
                cv2.destroyAllWindows()
                exit("结束")


