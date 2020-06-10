import os
import sys
#
# 将当前项目的目录加入临时环境变量，避免在其他地方运行时会出现引入错误
base_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(base_path)

import unittest
from BeautifulReport import BeautifulReport as BetRep
from conf import setting
from lib import set_cases

# 先生成测试用例文件
# set_cases.generate_test_file()

discover = unittest.defaultTestLoader.discover(
    start_dir=os.path.join(setting.BASE_PATH, 'testcases'),
    #pattern='test_get_user_info.py'
    pattern='*.py'
)

runner = BetRep(discover)
title = '接口测试'
runner.report(title, filename='its_report', log_path=os.path.join(setting.BASE_PATH, 'report'))
