import os
from dotenv import load_dotenv

# 启动时自动读取项目根目录下的 .env 文件
load_dotenv()


class Settings:
    """集中管理所有环境变量配置"""

    # 应用配置
    APP_NAME = os.getenv("APP_NAME", "Enterprise AI Agent Service")
    APP_VERSION = os.getenv("APP_VERSION", "1.0.0")

    # MySQL 数据库配置
    DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "")
    DB_NAME = os.getenv("DB_NAME", "enterprise_ai")


# 全局唯一实例，其他模块通过下面这行引用配置
settings = Settings()