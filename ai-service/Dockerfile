# 企业智能情报平台 - AI 服务 Docker 镜像
# 基于 Python 3.11 精简镜像
FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 先复制依赖清单并安装（利用 Docker 缓存：改代码不用重新装依赖）
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

# 复制项目代码
COPY . .

# 暴露端口
EXPOSE 8000

# 启动 FastAPI（0.0.0.0 让容器外部能访问）
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
