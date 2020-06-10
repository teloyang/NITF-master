"""
GetAllCases 获取data中所有excel中的用例
APICases 一个excel中的sheet页的用例生成一个对象，主要用于生成测试用例文件。一个测试用例文件对应excel中的一个sheet页
Case 处理每一个具体的用例（一行），配合unittest生成测试用例的执行过程。主要实现测试用例的数据、断言、依赖等

用例中的依赖处理：
设定参数规则为 $p{}, $r{}, $s{}
$p{id:data.uuid}, 表示需要获取依赖数据，id：表示依赖的用例id， data.uuid表示依赖用例的Response中的字段所在层级
ex: $p{use_login1:data.uuid}， 表示需要从用例ui为use_login1响应中的json数据中data对象中的uuid的值
    use_login1的响应 {"res":200, "data":{"uuid":"xxx", token="yyy"}}。则可以获取到xxx
data.uuid为jsonpath的查找规则，更多查找规则请查阅：https://pypi.org/project/jsonpath-rw/

$r{x}, 内容为空的参数表示此处需要添加随机字符，主要用于有唯一性检查的地方
处理过程为默认添加4位随机的ascII字符（大小写字母和数字）
x 为全局的变量，如果在第一个用例（任意地方）设置了$r{x}，那么任意地方使用$r{x}都会和第一个用例中的随机数一样
当需要使用不同的随机数时，需要修改x参数的值，如$r{xyz}

$s{}, 表示此处需要查询数据库，参数内容为SQL语句
目前仅支持一条SQL查询一个字段内容，如 uuid=$s{select uuid from user where username='nemo'}

# 关于用例文件的说明
一个sheet页为一个用例文件，多少个excel文件不重要，但是可以通过excel文件的名称进行模糊匹配
也就是如果只想执行某部分用例的话，可以统一命名。具体模糊匹配的设置在setting.py文件中的FILE_NAME = ''设置项
通配格式与discover类似，用*号作为通配符。比如 *login*，表示匹配所有文件名中包含login的文件
默认查找路径为当前项目的data文件夹，当然也可以修改，配置在setting.py的CASE_PATH中

excel用例必须参照login.xlsx格式，第一行为说明，实际用例从第三行开始
"""
import xlrd
import os
import re
import glob
import json
import random
import string
from conf import setting
from lib import utils
from jsonpath_rw import jsonpath, parse


# 全局变量，用于存储随机数
random_data = {}


class GetAllCases:
    """
    从cases文件夹中查找所有的测试用例，包括excel文件以及所有sheet页
    """
    @staticmethod
    def get_all_cases():
        """
        查找setting.py中配置的CASE_PATH路径中的所有xlsx文件，或者根据file_path中提供的通配符去查找用例文件
        :return: 返回找到的所有sheet页
        """
        # 根据配置文件中设置的文件查找规则查找excel文件
        file_path = setting.FILE_NAME
        sheet_cases = []
        if not file_path:
            case_files = [os.path.join(setting.CASE_PATH, file) for file in os.listdir(setting.CASE_PATH)
                          if file.endswith('.xls') or file.endswith('.xlsx')]
            '''
            ###输出的结果是所有测试用例的完整路径
            '''

        else:
            file_path = os.path.join(setting.CASE_PATH, file_path)
            '''
            ###拼接setting.CASE_PATH和file_path两个变量的值，连个变量之间的值用“\”隔离
            '''
            case_files = glob.glob(file_path)
        # 逐个打开excel文件
        for case_file in case_files:

            try:
                excel = xlrd.open_workbook(case_file)
                for sheet in excel.sheets():
                    '''
                    将excel.sheets()中的值，依次赋给sheet变量
                    excel.sheets()的格式是数组[<xlrd.sheet.Sheet object at 0x000001FC23E32F98>, <xlrd.sheet.Sheet object at 0x000001FC23E32E48>]
                    执行语句后，sheet变量数据的格式是<xlrd.sheet.Sheet object at 0x000001CB24E32F98>
                    '''
                    api_case = APICases(sheet)
                    sheet_cases.append(api_case)
                print('打开 《%s》 用例文件成功！' % case_file)
            except Exception:
                print('测试用例文件《%s》打开失败！' % case_file)
        return sheet_cases


class APICases:
    """
    处理每个sheet页中的用例
    """
    def __init__(self, sheet):
        self.sheet = sheet
        self.sheet_name = self.sheet.name
        # 接口名称
        self.doc = self.sheet.row_values(0)

    def get_cases(self):
        """
        self.sheet.nrows 是获取当前sheet页所有的行数
        获取当前sheet页中的所有用例，一行为一条用例
        :return: 以列表形式返回当前页所有用例
        """
        cases = []
        for row in range(2, self.sheet.nrows):
            cases.append(dict(zip(self.sheet.row_values(1), self.sheet.row_values(row))))
        return cases

class Case:
    """
    处理单个测试用例
    """
    def __init__(self, case):
        """
        接收的是excel中的一行，也就是单个用例
        根据所在字段转化为对象，以便后续使用和处理
        :param case:
        """
        # 用例id
        self.id = case.get('id')
        # 接口名称
        self.api_name = case.get('api_name')
        # 接口方法 POST GET
        self.method = case.get('method')
        # 接口链接
        self.url = case.get('url')
        # 用例描述
        self.desc = case.get('case_desc')
        # 请求数据
        self.data = case.get('data')
        # 检查数据
        self.check = case.get('check')
        # 用于检查字段是否有参数的正则表达式对象
        self.param_re = re.compile(r'\$([s|p|r])\{(.*?)\}')

    @staticmethod
    def get_data_dict(data):
        """
        # TODO: 小白接口要求密码传输过程采用MD5加密，可根据实际情况修改
        将传入的data，处理为字典格式
        :param data: 格式为"a=1,b=2,c=3"这种逗号分隔的等式
        :return: 返回字典格式的数据{"a":1, "b":2, "c":3}
        """
        if not data:
            return
        res = {}
        data = [d.strip() for d in data.split(setting.SEP) if d]
        for d in data:
            k, v = d.split('=')
            #如果报文中涉及密码，需要进行加密传输
            if setting.IS_MD5 and k in setting.MD5_FIELDS:
                v = utils.set_md5(v)
            res[k] = v
        return res

    @staticmethod
    def get_response_data(v, data):
        """
        处理响应数据，主要是从响应数据中获取依赖需要的数据
        :param v: 依赖的字段，如 uuid:data.uuid 表示依赖其他用例的参数是uuid, 然后uuid的层级是data.uuid
        :param data: 对应依赖用例的响应体
        :return: 从依赖用例的响应体中提取出的对应依赖字段的数据
        """
        json_exe = parse(v)
        if not isinstance(data, dict):
            try:
                data = json.loads(data)
                result = [match.value for match in json_exe.find(data)][0]
                return result
            except TypeError:
                raise ValueError('未能获取有效参数或给予的JSON路径不对，请检查参数设置！')

    @staticmethod
    def set_random_data(v, num=4):
        """
        生成随机字符串，返回字典{v: random_str}
        :param v: 用于标识随机变量，如$r{x}，x即使一个随机变量
        :param num: 生成的字符串长度，默认4个字符
        :return:
        """
        d = {}
        value = ''.join(random.sample(string.ascii_letters + string.digits, num))
        d[v] = value
        return d

    def _re_attr(self, attr, res):
        """
        通过正则表达式查找用例字段中是否存在参数，如果有参数则使用运算出的实际的值替换掉参数
        思路：使用正则表达式提取出当前字段中的所有参数。逐一进行处理，比如需要响应数据的、随机数、SQL查询结果的，在获取到这些数据
        后，采用正则表达式中的sub方法替换掉其中的第一个参数，一次只处理一个参数，通过for循环将所有参数替换为实际的值
        :param attr: 字段的值，也就是excel中的一个单元格，当然实际参数应该只会出现在url，请求（data）和预期结果（check）三个字段中
        :param res: 依赖用例的响应数据
        :return:
        """
        params = self.param_re.findall(attr)
        if params:
            # 根据findall找到的所有参数，确定需要替换的次数
            for i in range(len(params)):
                # 先处理参数, 如果参数存在，则找到之后的形式为[('p', 'id:data.uuid'),('r', ''), ('s', 'select * from ...')]
                k, v = params[i]
                if k == 'p':
                    # 如果是$p{}参数形式, 则需要从依赖用例的响应中获取实际数据
                    try:
                        case_id, value = v.split(':')
                        value = self.get_response_data(value, res.get(case_id))
                    except IndexError:
                        raise ValueError('未能从指定用例的响应中取回依赖数据，请检查参数设置或用例的执行顺序！')
                    # 将值替换第一个参数
                    attr = self.param_re.sub(str(value), attr, 1)
                elif k == 'r':
                    # 如果参数是$r{}形式,则使用随机函数生成的4个字符替换
                    # value = ''.join(random.sample(string.ascii_letters+string.digits, num))
                    # 如果全局变量random_data中已存在$r{key}相同的key，则重用之前的随机数
                    if v not in random_data:
                        random_data.update(self.set_random_data(v))
                        value = random_data.get(v)
                    else:
                        value = random_data.get(v)
                    attr = self.param_re.sub(str(value), attr, 1)
                elif k == 's':
                    # 如果参数是$s{}, 则需要执行其中的SQL语句
                    # sql = self._re_attr(v, res)
                    value = utils.get_data_by_sql(v)
                    if not value:
                        value = 'null'
                    attr = self.param_re.sub(str(value), attr, 1)
        return attr

    def get_url(self, res):
        """
        在URL中找是否有参数，如果有参数，则计算参数的值并更新URL
        :return:
        """

        if self.url:
            # 去前后空格
            self.url = self.url.strip()
        else:
            raise ValueError('用例中没有有效的url，请检查url字段。')
        return self._re_attr(self.url, res)

    def get_data(self, res):
        """
        # TODO: 小白接口需要签名，签名设置函数为utils.set_request_data，可根据实际情况修改
        处理请求数据
        1）如果请求数据是s=App.User.Login,username=first,password=asdf1234，
        处理为{'s': 'App.User.Login', 'username': 'first', 'password': '1ADBB3178591FD5BB0C248518F39BF6D'}
        2）如果请求直接就是{“s”: “App.User.Login”, “username”: “first”, “password”: “1ADBB3178591FD5BB0C248518F39BF6D”}
        则直接作为json数据处理
        :return: 返回请求需要的数据
        """
        if self.data:
            self.data = self.data.strip()
            self.data = self._re_attr(self.data, res)
            # 如果data字段类似{"a":1, "b":2}这种格式，那么认为这是一个json格式的数据
            if self.data.startswith('{') and self.data.endswith('}'):
                try:
                    data = json.loads(self.data, encoding='utf-8')
                    for field in setting.MD5_FIELDS:
                        need_md5 = data.get(field)
                        if need_md5:
                            data[field] = utils.set_md5(need_md5)
                    # 如果不需要签名
                    if setting.IS_SIGN:
                        return utils.set_request_data(data)
                    else:
                        return data
                except Exception:
                    raise ValueError('用例id:%s 字段data中的数据不是有效的JSON格式数据，请检查！')
            # 否则依然是=格式，则进行拆分处理
            else:
                if setting.IS_SIGN:
                    return utils.set_request_data(self.get_data_dict(self.data))
                else:
                    return self.get_data_dict(self.data)

    def get_check(self, res):
        """
        将“ret=400,msg=客户端非法请求：缺少必要参数password”这种格式的预期结果，
        拆分成列表['ret=400','msg=客户端非法请求：缺少必要参数password'],以便测试用例中处理
        :return: 如['ret=400','msg=客户端非法请求：缺少必要参数password']
        """
        if self.check:
            self.check = self._re_attr(self.check, res)
            return [c for c in self.check.split(setting.SEP) if c]
        else:
            raise ValueError('测试用例中不能没有结果检查！')
