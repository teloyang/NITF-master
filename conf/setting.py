import os
import pymysql


API_URL = 'https://immgmt.88hmf.com/bctalk-mgmt/admin/login'

# 是否需要签名
IS_SIGN = False

# 密码是否要加密
IS_MD5 = False
# 需要加密的参数名
MD5_FIELDS = {'password', }

# 路径配置
BASE_PATH = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__)))
###os.path.abspath(__file__):获取当前脚本的完整路径,这条代码获取的是整个文件的目录
# excel测试用例存放位置
CASE_PATH = os.path.join(BASE_PATH, 'data')
###拼接BASE_PATH和“data”
# unittest测试用例文件存放位置
TEST_PATH = os.path.join(BASE_PATH, 'testcases')
# 测试报告路径
REPORT_PATH = os.path.join(BASE_PATH, 'report')

# 测试时自动查找excel用例文件的通配符
FILE_NAME = ''
# 定义excel中data与check的分隔符，可更换为回车符\n等易识别且不会在参数值中出现的符号
SEP = ';'

APP_KEY = ''
APP_SECRET = ''



