# -*- coding: utf-8 -*-
# ------------------------------------------------
#   python终端显示彩色字符类，可以调用不同的方法
# 选择不同的颜色.使用方法看示例代码就很容易明白.
# ------------------------------------------------
#
# 显示格式: \033[显示方式;前景色;背景色m
# ------------------------------------------------
# 显示方式             说明
#   0                 终端默认设置
#   1                 高亮显示
#   4                 使用下划线
#   5                 闪烁
#   7                 反白显示
#   8                 不可见
#   22                非粗体
#   24                非下划线
#   25                非闪烁
#
#   前景色             背景色            颜色
#     30                40              黑色
#     31                41              红色
#     32                42              绿色
#     33                43              黃色
#     34                44              蓝色
#     35                45              紫红色
#     36                46              青蓝色
#     37                47              白色
# ------------------------------------------------
class printcon:
    HEADER = '\033[31m'
    QUESTION = '\033[94m'
    RESULT = '\033[92m'
    ANALYSIS = '\033[93m'
    NORMAL = '\033[91m'
    ENDC = '\033[37m'
    ENDC_GREEN = '\033[46m'

    def start(self,color):
        if color=='header':
            print(self.HEADER)
        elif color=='question':
            print(self.QUESTION)
        elif color == 'result':
            print(self.RESULT)
        elif color=='analysis':
            print(self.ANALYSIS)
        else:
            print(self.NORMAL)

    def endwhite(self):
        print(self.ENDC)

    def endgreen(self):
        print(self.ENDC_GREEN)

    def disable(self):
        self.HEADER = ''
        self.OKBLUE = ''
        self.OKGREEN = ''
        self.WARNING = ''
        self.FAIL = ''
        self.ENDC = ''