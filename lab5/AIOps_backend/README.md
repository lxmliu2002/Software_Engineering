# 智能运维系统（后端）

## 介绍

智能运维系统——后端部分

## 环境配置

环境配置流程如下：

1. 使用`mysql`新建数据库`ai_ops`。

2. 在环境变量中添加变量`MYSQL_PWD`，值设置为`mysql`的`root`用户密码。

3. 下载[redis](https://github.com/tporadowski/redis/releases)，windows中zip压缩包。

4. 解压，进入文件夹中，打开命令行，输入`./redis-server.exe redis.windows.conf`。

5. 安装`python`依赖项
    * 这里的`requirements.txt`，是我在配环境的时候安装的，从新建虚拟环境开始的，可以直接安装 `pip install -r requirements.txt`。
    
6. 进入项目根目录，迁移数据库：

    ```shell
    python manage.py makemigrations
    python ./manage.py migrate
    ```

7. 在后台启动ollama，并安装 `gemma2:9b` 模型

8. 运行程序：`python .\manage.py runserver`
