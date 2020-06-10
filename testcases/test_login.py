import json

import ddt
import requests
import unittest
from lib.get_data import Case
from lib.set_cases import cases
from lib import utils


@ddt.ddt
class Login(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.response = dict()

    @ddt.data(*cases.get('Login'))
    def test_login(self, data):
        HEADERS = {'Content-Type': 'application/json'}
        case = Case(data)

        self._testMethodDoc = case.desc

        url = case.get_url(self.response)

        # 获取请求数据
        data = case.get_data(self.response)
        data_json = json.dumps(data)
        # 获取结果检查数据
        check = case.get_check(self.response)

        print('接口地址为：%s' % url)

        print('请求数据为：%s' % data)

        if case.method.lower() == 'post':
            r = requests.post(case.url, headers=HEADERS, data=data_json)
            res = r.text
        elif case.method.lower() == 'get':
            r = requests.get(case.url, params=data)
            res = r.text
        elif case.method.lower() == 'put':
            r = requests.put(case.url, params=data)
            res = r.text
        else:
            raise ValueError('请选择get或post方式, 目前仅支持这两种方式。')
        # 将结果以字典存储在属性中
        self.response[case.id] = res

        print('断言检查数据为：%s' % check)
        print('服务器返回结果为：%s' % res)

        res = utils.set_res_data(res)

        for c in check:
            self.assertIn(c.lower(), res.lower(),
                          "结果校验失败：预期结果 %s， 实际结果 %s" % (c, res))
