import os
from lib.get_data import GetAllCases
from conf import setting

# 全局变量，打开所有用例文件
all_cases = GetAllCases().get_all_cases()



def _generate_file(sheet_name):
    """
    生成python测试用例文件， 一个sheet页对应一个unittest测试用例类文件
    :param sheet_name: sheet页名称
    :return:
    """
    file_name = 'test_%s.py' % sheet_name.lower()
    template_file = os.path.join(setting.BASE_PATH, 'conf', 'template.txt')
    with open(template_file, 'r', encoding='utf-8') as template:
        content = template.read().format(class_name=sheet_name.replace('_', ''),
                                         data_name=sheet_name,
                                         method_name=sheet_name.lower())
        with open(os.path.join(setting.TEST_PATH, file_name), 'w', encoding='utf-8') as py:
            py.write(content)


def _delete_test_file(path):
    """
    删除指定目录下的所有文件，主要用于生成测试用例文件前，先清除已有的测试用例文件。
    以便每次运行都是运行想要运行的用例。
    :param path:
    :return:
    """
    ls = os.listdir(path)
    for i in ls:
        c_path = os.path.join(path, i)
        if os.path.isdir(c_path):
            _delete_test_file(c_path)
        else:
            os.remove(c_path)


def set_test_ddt_data():
    """
    生成测试用例需要用到的参数化数据，返回的结果是一个字典{‘sheet页名’：{sheet数据}}，主要是为了测试用例ddt方便提取其中的数据
    :return: 返回是一个字典形式的数据{'sheet_name':[{}, {}]}
    """
    cases_dict = dict()
    for sheet_cases in all_cases:
        cases_dict[sheet_cases.sheet_name] = sheet_cases.get_cases()

    return cases_dict



def generate_test_file():
    """
    生成测试用例文件
    :return:
    """
    _delete_test_file(setting.TEST_PATH)
    for sheet_cases in all_cases:
        _generate_file(sheet_cases.sheet_name)


# 先准备好需要引入的数据，测试用例一经引入当前文件，就会先执行
cases = set_test_ddt_data()


