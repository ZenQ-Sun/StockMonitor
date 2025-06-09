# 使用官方的 Python 基础镜像
# Alpine Linux 镜像非常小巧，适合构建轻量级容器
# python:3.9-alpine 是一个常用的选择，这里以 3.9 为例，你可以根据你的项目需要选择其他版本
FROM python:3.9-alpine
ENV PYTHONNUMBUFFERED=1
ENV HTTP_PROXY=
ENV HTTPS_PROXY=
ENV TZ=Asia/Shanghai
ENV WEBHOOK=""
# 设置工作目录
# 容器启动后，所有的命令都会在这个目录下执行
WORKDIR /app

# 复制 requirements.txt 到容器的 /app 目录
# 这一步单独进行是为了利用 Docker 的构建缓存。
# 如果 requirements.txt 没有变化，Docker 就不需要重新安装依赖，可以加速构建。
COPY requirements.txt .

# 安装 Python 依赖包
# --no-cache-dir: 不缓存 pip 下载的包，减少镜像大小
# -r requirements.txt: 从 requirements.txt 文件中读取并安装依赖
# 注意：对于某些需要编译的包，可能需要安装 build-base 或其他开发库。
# 如果遇到安装失败，可以尝试在 RUN pip install 前添加：
# RUN apk add --no-cache build-base linux-headers
RUN pip install --no-cache-dir -r requirements.txt

# 复制整个应用代码到容器的 /app 目录
# 这一步放在安装依赖之后，同样是为了利用缓存。
# 只有当你的应用代码发生变化时，这一层才需要重新构建。
COPY . .

# 如果你的应用需要监听某个端口，请暴露它
# EXPOSE 8000 # 示例：如果你的 Flask/Django 应用运行在 8000 端口

# 定义容器启动时要执行的命令
# CMD ["python", "your_app_name.py"] # 运行一个 Python 脚本
# 或者如果你使用的是 Flask/Django 等框架，可能需要指定框架的启动命令
# CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "your_project.wsgi:application"] # Django 示例
# CMD ["flask", "run", "--host=0.0.0.0", "--port=8000"] # Flask 示例 (开发环境，生产环境不推荐直接用 flask run)
# 请根据你的实际应用入口进行修改
CMD ["python", "StockInfo.py"]