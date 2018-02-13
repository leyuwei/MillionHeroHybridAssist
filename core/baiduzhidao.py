# -*- coding: utf-8 -*-

"""

    Baidu zhidao searcher

"""
import operator
import re
import random
import requests
from html.parser import HTMLParser

from config import reg

Agents = (
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
)


def baidu_count(keyword, answers, numofquery=10, delword='', timeout=2):
    """
    Count the answer number from first page of baidu search

    :param keyword:
    :param timeout:
    :return:
    """
    """
    headers = {
        "Host": "zhidao.baidu.com",
        "User-Agent": random.choice(Agents)
    }
    params = {
        "word": keyword.encode("gbk"),
        "rn": str(numofquery).encode("gbk"),
        "ie": "gbk".encode("gbk")
    }
    """
    headers = {
        "Host": "www.baidu.com",
        "User-Agent": random.choice(Agents)
    }
    params = {
        "wd": keyword.encode("utf-8"),
        "rn": "10".encode("utf-8")
    }
    resp = requests.get("http://www.baidu.com/s", params=params, headers=headers, timeout=timeout)

    #resp = requests.get("https://zhidao.baidu.com/search", params=params, headers=headers, timeout=timeout)

    newanswers = [ans.replace(delword,"") for ans in answers]

    if not resp.ok:
        print("百度搜索出错或超时")
        return {
            ans: 0
            for ans in answers
        }

    dr = re.compile(r'<[^>]+>', re.S)
    html = resp.content
    #html_doc = str(html, 'utf-8')
    html_doc = resp.text
    resptext = dr.sub('', html_doc)
    resptext = re.sub(reg, "", resptext)
    resptext = resptext.replace(' ', '')
    resptext = resptext.replace(delword, "")
    resptext = resptext.lower()
    summary = {
        ans: resptext.count(ans2)
        for (ans,ans2) in zip(answers,newanswers)
    }
    
    if all([cnt == 0 for cnt in summary.values()]):
        return summary

    default = list(summary.values())[0]
    if all([value == default for value in summary.values()]):
        answer_firsts = {
            ans: resptext.count(ans2)
            for (ans, ans2) in zip(answers, newanswers)
        }
        sorted_li = sorted(answer_firsts.items(), key=operator.itemgetter(1), reverse=False)
        answer_li, index_li = zip(*sorted_li)
        return {
            a: b
            for a, b in zip(answer_li, reversed(index_li))
        }
    return summary


# 定义一个MyParser继承自HTMLParser
class MyParser(HTMLParser):
    re = []  # 放置结果
    flg = 0  # 标志，用以标记是否找到我们需要的标签
    upperbound = 4 # 存储解答数量上限
    anscount = 0 # 解答累积计数

    def __init__(self):
        HTMLParser.__init__(self)
        self.flg = 0
        self.re.clear()

    def handle_starttag(self, tag, attrs):
        tag = tag.strip()
        if tag == 'dd':  # 目标标签
            for attr in attrs:
                if attr[0] == 'class' and attr[1] == 'dd answer':  # 目标标签具有的属性
                    self.flg = 1  # 符合条件则将标志设置为1
                    break
        else:
            pass

    def handle_endtag(self, tag):
        tag = tag.strip()
        if tag == "dd":
            self.flg = 0

    def handle_data(self, data):
        if data and self.flg == 1:
            dr = re.compile(r'<[^>]+>', re.S)
            t = dr.sub('', data.strip())
            t = t.replace('\n','')
            t = t.replace('答：', '('+str(self.anscount+1)+')')
            self.anscount += 1

            if self.anscount <= self.upperbound:
                self.re.append(t)  # 如果标志为我们需要的标志，则将数据添加到列表中
            self.flg = 0  # 重置标志，进行下次迭代
        else:
            pass


def zhidao_tree(question, answers, timeout=2):
    allanswers = ' OR '.join(answers)
    allanswers = question + '(' + allanswers + ')'
    headers = {
        "Host": "zhidao.baidu.com",
        "User-Agent": random.choice(Agents)
    }
    params = {
        "word": allanswers.encode("gbk"),
        "ie": "gbk".encode("gbk")
    }
    resp = requests.get("https://zhidao.baidu.com/search", params=params, headers=headers, timeout=timeout)

    if not resp.ok:
        print("知道图谱搜索出错或超时")
        return {
            ans: 0
            for ans in answers
        }

    parser = MyParser()
    html = resp.content
    html_doc = str(html, 'GB18030') # Thanks to https://www.v2ex.com/t/303036 SoloCompany
    dr = re.compile(r'</?em>|<i[^>]+>|</i>', re.S) # 替换<em>标签、<i x=y>标签和</i>标签
    html_doc = dr.sub('', html_doc)
    parser.feed(html_doc)
    datastream = parser.re
    return datastream

def baidu_qmi_count(keyword, answers, numofquery=10, delword='', timeout=2):
    headers = {
        "Host": "www.baidu.com",
        "User-Agent": random.choice(Agents)
    }
    params = {
        "wd": keyword.encode("utf-8"),
        "rn": "10".encode("utf-8")
    }
    resp = requests.get("http://www.baidu.com/s", params=params, headers=headers, timeout=timeout)

    if not resp.ok:
        print("QMI百度搜索出错或超时")
        return {
            ans: 0
            for ans in answers
        }

    parser = MyParser()
    html = resp.content
    html_doc = str(html, 'utf-8')
    html_doc = re.findall(r'百度为您找到相关结果约([\w,]+?)个', html_doc)
    html_doc = html_doc[0].replace("，","")
    html_doc = html_doc.replace(",", "")
    return int(html_doc.strip())