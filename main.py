# -*- coding:utf-8 -*-

"""
    Million Heroes
"""


import multiprocessing
from multiprocessing import Event
from multiprocessing import Pipe

import win32api
from PIL import ImageFilter
from threading import Thread
import time
from argparse import ArgumentParser

import re
import operator
from functools import partial
from terminaltables import AsciiTable

from config import api_key
from config import api_version
from config import app_id
from config import app_key
from config import app_secret
from config import data_directory
from config import enable_chrome
from config import image_compress_level
from config import prefer
from config import crop_areas
from config import reg
from core.Colored import *
from core.android import analyze_current_screen_text
from core.android import save_screen
from core.Slicer import *
from core.ios import analyze_current_screen_text_ios
from core.baiduzhidao import baidu_count
from core.bingqa import bing_count
from core.zhihuqa import zhihu_count
from core.check_words import parse_false
from core.airplayscr import check_exsit
from core.chrome_search import run_browser
from core.ocr.baiduocr import get_text_from_image as bai_get_text
from core.ocr.spaceocr import get_text_from_image as ocrspace_get_text

global isNegativeQuestion
global origQuestion
isNegativeQuestion = False
origQuestion = ""
con = printcon()

if prefer[0] == "baidu":
    get_text_from_image = partial(bai_get_text,
                                  app_id=app_id,
                                  app_key=app_key,
                                  app_secret=app_secret,
                                  api_version=api_version,
                                  timeout=5)
elif prefer[0] == "ocrspace":
    get_test_from_image = partial(ocrspace_get_text, api_key=api_key)

def parse_args():
    parser = ArgumentParser(description="Million Hero Assistant")
    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=5,
        help="default http request timeout"
    )
    return parser.parse_args()

def parse_question_and_answer(text_list):
    global origQuestion
    question = ""
    start = 0
    for i, keyword in enumerate(text_list):
        question += keyword
        if "?" in keyword:
            start = i + 1
            break
        elif "？" in keyword: # 增加中文问号判断
            start = i + 1
            break
        if ":" in keyword:
            start = i + 1
            break
        elif "：" in keyword:
            start = i + 1
            break
        elif keyword.endswith("."):
            start = i + 1
            break
        elif keyword.endswith("。"):
            start = i + 1
            break
        elif "哪" in keyword:
            start = i + 1
            break
        elif keyword.endswith("是"):
            start = i + 1
            break
    real_question = question.split(".")[-1]
    origQuestion = real_question
    # 新增题目模式识别
    global isNegativeQuestion
    isNegativeQuestion = False
    if real_question.find('没有')>=0 or real_question.find('未')>=0 or real_question.find('不是')>=0 or real_question.find('是错')>=0 or real_question.find('不属于')>=0 or real_question.find('不正确')>=0 or real_question.find('不对')>=0 or real_question.find('不适')>=0:
        isNegativeQuestion = True
        real_question = real_question.replace('没有','有')
        real_question = real_question.replace('未', '')
        real_question = real_question.replace('还未', '已')
        real_question = real_question.replace('不是', '是')
        real_question = real_question.replace('是错', '是对')
        real_question = real_question.replace('不属于', '属于')
        real_question = real_question.replace('不正确', '正确')
        real_question = real_question.replace('不对', '对')
        real_question = real_question.replace('不适', '适')
    question, true_flag = parse_false(real_question)
    # 增加识别异常符号处理
    for ii in range(start,len(text_list)):
        text_list[ii] = re.sub(reg, "", text_list[ii])
        text_list[ii] = text_list[ii].lower()
    return true_flag, real_question, question, text_list[start:]

def pre_process_question(keyword):
    """
    strip charactor and strip ?
    :param question:
    :return:
    """
    for char, repl in [("“", ""), ("”", ""), ("？", "")]:
        keyword = keyword.replace(char, repl)
    keyword = keyword.split(r"．")[-1]
    keywords = keyword.split(" ")
    keyword = "".join([e.strip("\r\n") for e in keywords if e])
    return keyword

class SearchThread(Thread):
    def __init__(self, question,answer,timeout,delword,engine):
        Thread.__init__(self)
        self.question = question
        self.answer = answer
        self.timeout = timeout
        self.engine = engine
        self.delword = delword
    def run(self):
        if self.engine == 'baidu':
            self.result = baidu_count(self.question,self.answer,delword=self.delword,timeout=self.timeout)
        elif self.engine == 'bing':
            self.result = bing_count(self.question,self.answer,delword=self.delword,timeout=self.timeout)
        elif self.engine == 'zhihu':
            self.result = zhihu_count(self.question, self.answer,delword=self.delword, timeout=self.timeout)
        else:
            self.result = zhihu_count(self.question, self.answer,delword=self.delword, timeout=self.timeout)
    def get_result(self):
        return self.result

def main():
    args = parse_args()
    timeout = args.timeout

    if enable_chrome:
        closer = Event()
        noticer = Event()
        closer.clear()
        noticer.clear()
        reader, writer = Pipe()
        browser_daemon = multiprocessing.Process(
            target=run_browser, args=(closer, noticer, reader,))
        browser_daemon.daemon = True
        browser_daemon.start()

    def __inner_job():
        global isNegativeQuestion,origQuestion
        start = time.time()
        if game_platform==2:
            text_binary = analyze_current_screen_text(
                directory=data_directory,
                compress_level=image_compress_level[0],
                crop_area = crop_areas[game_type]
            )
        else:
            text_binary = analyze_current_screen_text_ios(
                directory=data_directory,
                compress_level=image_compress_level[0],
                crop_area=crop_areas[game_type]
            )
        keywords = get_text_from_image(
            image_data=text_binary,
        )
        if not keywords:
            print("本题不能识别，请尽快自行作答！")
            return

        true_flag, real_question, question, answers = parse_question_and_answer(keywords)
        orig_answer = answers
        # 分词预处理
        allanswers = ''
        for i in answers:
            allanswers = allanswers + i
        repeatanswers = get_repeat_num_seq(allanswers)
        maxlen = 0
        delword = '' # 预分词目标：找到选项中的重复部分，提升选项之间的差异性
        for (d,x) in repeatanswers:
            if x>=3 and len(d)>maxlen:
                maxlen = len(d)
                delword = d

        print("")
        print("*" * 40)
        print('题目： ' + origQuestion)
        print("*" * 40)

        # notice browser
        if enable_chrome:
            writer.send(question)
            noticer.set()

        search_question = pre_process_question(question)
        search_question_1 = search_question + " " + answers[0].replace(delword,"")
        search_question_2 = search_question + " " + answers[1].replace(delword,"")
        search_question_3 = search_question + " " + answers[2].replace(delword,"")
        thd1 = SearchThread(search_question, answers, timeout, delword, 'baidu')
        thd2 = SearchThread(search_question, answers, timeout, delword, 'bing')
        thd3 = SearchThread(search_question, answers, timeout, delword, 'zhihu')
        thd4 = SearchThread(search_question_1, answers, timeout, delword, 'baidu')
        thd5 = SearchThread(search_question_2, answers, timeout, delword, 'baidu')
        thd6 = SearchThread(search_question_3, answers, timeout, delword, 'baidu')

        # 创立3并发线程
        if __name__ == '__main__':
            thd1.setDaemon(True)
            thd1.start()
            thd2.setDaemon(True)
            thd2.start()
            thd3.setDaemon(True)
            thd3.start()
            thd4.setDaemon(True)
            thd4.start()
            thd5.setDaemon(True)
            thd5.start()
            thd6.setDaemon(True)
            thd6.start()
            # 顺序开启3线程
            thd1.join()
            thd2.join()
            thd3.join()
            thd4.join()
            thd5.join()
            thd6.join()
            # 等待3线程执行结束
        summary = thd1.get_result()
        summary2 = thd2.get_result()
        summary3 = thd3.get_result()
        summary4 = thd4.get_result()
        summary5 = thd5.get_result()
        summary6 = thd6.get_result()
        # 获取线程执行结果

        # 下面开始合并结果并添加可靠性标志
        creditFlag = True
        credit = 0
        summary_t = summary
        for i in range(0,len(summary)):
            summary_t[answers[i]] += summary2[answers[i]]
            summary_t[answers[i]] += summary3[answers[i]]
            credit += summary_t[answers[i]]

        if credit < 2:
            creditFlag = False

        if isNegativeQuestion == False:
            summary_li = sorted(summary_t.items(), key=operator.itemgetter(1), reverse=True)
        else:
            summary_li = sorted(summary_t.items(), key=operator.itemgetter(1), reverse=False)
        data = [("选项", "权重")]
        topscore = 0
        for a, w in summary_li:
            if w > topscore:
                topscore = w
        for a, w in summary_li:
            if isNegativeQuestion==False:
                data.append((a, w))
            else:
                data.append((a, topscore-w))
        table = AsciiTable(data)
        print(table.table)
        print("")

        end = time.time()
        print("*" * 40)
        print("分析结果 耗时 {0} 秒".format("%.1f" % (end - start)))
        print("*" * 40)
        print("")
        if creditFlag == False:
            print("！！！ 本题预测结果不是很可靠，请慎重  ！！！\n")
        if isNegativeQuestion==True:
            print("--- 本题是否定提法，程序已帮您优化结果！ ---\n")
        if true_flag:
            print("      √ 建议选项 ： ", summary_li[0][0],' (第',orig_answer.index(summary_li[0][0])+1,'项)')
            print("      × 排除选项 ： ", summary_li[-1][0])
        else:
            print("      √ 建议选项 ： ", summary_li[0][0])
            print("      × 排除选项 ： ", summary_li[-1][0])

        # 测试：新匹配算法
        summary_newalg = dict()
        summary_newalg.update({orig_answer[0] : summary5[orig_answer[0]] + summary6[orig_answer[0]]})
        summary_newalg.update({orig_answer[1]: summary4[orig_answer[1]] + summary6[orig_answer[1]]})
        summary_newalg.update({orig_answer[2]: summary4[orig_answer[2]] + summary5[orig_answer[2]]})
        if isNegativeQuestion == False:
            summary_li2 = sorted(summary_newalg.items(), key=operator.itemgetter(1), reverse=True)
        else:
            summary_li2 = sorted(summary_newalg.items(), key=operator.itemgetter(1), reverse=False)
        print("")
        print("      * (测试)相似算法建议 ： ", summary_li2[0][0],' (第',orig_answer.index(summary_li2[0][0])+1,'项)')
        if orig_answer.index(summary_li2[0][0]) == orig_answer.index(summary_li[0][0]):
            print("      新旧算法解答一致，建议选择 第",orig_answer.index(summary_li[0][0])+1,"项 答案！")

        save_screen(
            directory=data_directory
        )

    print("""
    原作者：GitHub/smileboywtu forked since 2018.01.10
    Branch版本：V3.6 已与原作者Repo有较大不同
    Branch作者：GitHub/leyuwei
    Branch改进： 图像预增强以提升识别准确率
                修正提问问题的判断
                修正正则过滤表达式
                优化结果显示效果
                新增分词
                (测试)全新匹配算法
    请选择答题节目: 
      1. 百万英雄
      2. 冲顶大会
    """)
    game_type = input("输入游戏编号: ")
    if game_type == "1":
        game_type = '百万英雄'
    elif game_type == "2":
        game_type = '冲顶大会'
    else:
        game_type = '百万英雄'

    print("""
    操作平台的一些说明：如果您是iOS，则必须使用您的电脑创建WiFi热点并将您的iOS设备连接到该热点，
                      脚本即将为您打开投屏软件，您需要按照软件的提示进行操作。
                      如果您使用的是Android则无需担心，将您的设备使用数据线连接电脑，开启Adb
                      调试即可正常使用该脚本。
    请选择您的设备平台：
            1. iOS
            2. Android
    """)

    game_platform = input("输入平台编号: ")
    if game_platform == "1":
        game_platform = 1
        if check_exsit()==0:
            print("正在唤醒投屏软件，请同意管理员权限并按照软件要求将您的iOS设备投放在电脑屏幕上，最后再回到该脚本进行操作。")
            win32api.ShellExecute(0, 'open', 'airplayer.exe', '', '', 0)
        else:
            print("投屏软件已经启动。")
    elif game_platform == "2":
        game_platform = 2
    else:
        game_platform = 1

    while True:
        print("""
    -----------------------------
    请在答题开始前运行程序，
    答题开始的时候按Enter预测答案
                """)

        enter = input("按Enter键开始，按ESC键退出...")
        if enter == chr(27):
            break
        try:
            __inner_job()
        except Exception as e:
            print("截图分析过程中出现故障，请确认设备是否连接正确（投屏正常），网络是否通畅！")

    if enable_chrome:
        reader.close()
        writer.close()
        closer.set()
        time.sleep(3)


if __name__ == "__main__":
    main()
