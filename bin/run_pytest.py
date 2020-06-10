import os
import sys
import subprocess
# 将当前项目目录加入临时环境变量，避免在其他地方运行时会出现引入错误
base_path = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)
sys.path.append(base_path)

from lib.set_cases import generate_test_file
from conf import setting


# 先重新生成测试用例
generate_test_file()

if __name__ == '__main__':
    # --reruns 3 用例失败重试3次
    # --reruns-delay 1 重试次数之间间隔1秒
    cmd = 'pytest {test_path}  --html={report_path}/report.html --reruns 3 --reruns-delay 1'.format(
        test_path=setting.TEST_PATH,
        report_path=setting.REPORT_PATH
    )
    # pytest.main([test_path, '--html=report.html'])
    subprocess.run(cmd)
