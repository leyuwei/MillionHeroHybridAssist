# -*- coding: utf-8 -*-

"""

    SO searcher

"""
import operator
import re
import random
import requests

from config import reg

Agents = (
    "Mozilla/5.0 (X11; Fedora; Linux x86_64; rv:57.0) Gecko/20100101 Firefox/57.0",
    "Mozilla/5.0 (X11; Fedora; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36"
)


def so_count(keyword, answers, delword='', timeout=2):
    """
    Count the answer number from first page of baidu search

    :param keyword:
    :param timeout:
    :return:
    """
    headers = {
        "Host": "www.so.com",
        "User-Agent": random.choice(Agents)
    }
    params = {
        "q": keyword.encode("utf-8"),
        "ie": "utf-8".encode("utf-8")
    }
    resp = requests.get("https://www.so.com/s", params=params, headers=headers, timeout=timeout)

    newanswers = [ans.replace(delword, "") for ans in answers]

    if not resp.ok:
        print("360搜索出错或超时")
        return {
            ans: 0
            for ans in answers
        }

    dr = re.compile(r'<[^>]+>', re.S)
    resptext = dr.sub('', resp.text)
    resptext = re.sub(reg, "", resptext)
    resptext = resptext.replace(' ', '')
    resptext = resptext.replace(delword, "")
    resptext = resptext.lower()
    summary = {
        ans: resptext.count(ans2)
        for (ans, ans2) in zip(answers, newanswers)
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
