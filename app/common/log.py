import os
import os
import sys
import traceback

from loguru import logger

from app.common.config import VERSION


class MyLogger:
    def __init__(self, log_file_dir):
        self.log_file_path = log_file_dir + VERSION + '.log'
        self.logger = logger
        self.logger.remove()

        self.logger.add(sys.stdout,
                        # 颜色>时间
                        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                        # 模块名.方法名
                               "<cyan>{module}</cyan>.<cyan>{function}</cyan>"
                               ":<cyan>{line}</cyan> | "  # 行号
                               "<level>{level}</level>: "  # 等级
                               "<level>{message}</level>",  # 日志内容
                        )
        # 输出到文件的格式
        self.logger.add(self.log_file_path,
                        format='{time:YYYY-MM-DD HH:mm:ss} - '  # 时间
                               "{process.name} | "  # 进程名
                               "{thread.name} | "  # 进程名
                        # 模块名.方法名:行号
                               '{module}.{function}:{line} - {level} -{message}',
                        rotation="10 MB")

    def get_logger(self):
        return self.logger


def my_excepthook(type, value, tb):
    trace = ''.join(traceback.format_exception(type, value, tb))
    logger.exception(f"An unhandled exception occurred: {trace}")
    logs.error("程序因异常崩溃：sys.exit(1)")
    sys.exit(1)


sys.excepthook = my_excepthook

# 设置日志
logs = MyLogger( os.path.join(os.path.dirname(sys.argv[0]), 'log/')).get_logger()
