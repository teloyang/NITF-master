import hashlib
import sqlite3
from conf.setting import *


def set_request_data(params, key=None, secret=None):
    """
    # TODO: 接口需要签名，签名设置函数utils.set_request_data，可根据实际情况修改
    根据小白接口的规则生成签名
    :param params: 请求中的所有参数
    :param key:
    :param secret:
    :return:
    """
    if not params:
        params = {}
    key = key or APP_KEY
    secret = secret or APP_SECRET
    params.pop('app_secret', None)
    params['app_key'] = key
    params_str = (''.join([str(params[value]) for value in sorted([key for key in params])])
                  + secret).encode('utf-8')
    md5_ctx = hashlib.md5()
    md5_ctx.update(params_str)
    params['sign'] = md5_ctx.hexdigest().upper()
    return params


def set_md5(pwd):
    """
    # TODO: 小白接口密码采用MD5加密，可根据实际情况修改
    通过MD5加密传输的密码
    :param pwd:
    :return:
    """
    md5 = hashlib.md5()
    if pwd:
        md5.update(pwd.encode('utf-8'))
        return md5.hexdigest().upper()
    #将PWD进行加密，并且将返回的hash码中小写字母更换为大写字母
    else:
        return


def set_res_data(res):
    """
    返回的报文是json格式的，利用字符替换让数据变成"a=1,b=2"的格式
    :param res: Response的文本数据r.text
    :return:
    """
    return res.replace('":"', '=').replace('":', '=')


def get_data_by_sql(sql, *args):
    # TODO: 采用sqlite3作为演示，可根据需要修改
    with sqlite3.connect(SQL_CONFIG) as conn:
        cur = conn.cursor()
        return cur.execute(sql, args).fetchone()[0]


def get_datas_by_sql(sql, *args):
    # TODO: 采用sqlite3作为演示，可根据需要修改
    with sqlite3.connect(SQL_CONFIG) as conn:
        cur = conn.cursor()
        return cur.execute(sql, args).fetchall()


