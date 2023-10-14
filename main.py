"""
@author: got991
@file: main.py
@contact: 484029294@qq.com
@github: https://github.com/got991
@license: GNU General Public License v3.0
"""

# main.py_summary_
# Raises:
#     SystemError: 在不支持系统上时
#     Exception: _发生未知错误时（变量 ik 非正常值）
#     Exception: 版本核心 sha1 校验失败时
# Returns:
#     _type_: _description_

import logging
import time
import configparser
import json
import os
import hashlib
import platform
import wget
import rich
from rich.console import Console
import urllib
import ssl
import socket

# 帮助我们亲爱的 SSL 取消全局证书认证。
ssl._create_default_https_context = ssl._create_unverified_context
# 检测系统 (Windows / Linux)
system = platform.platform().lower()
if "windows" in system or "nt" in system:
    SystemType = "Windows"
elif "linux" in system:
    SystemType = "Linux"
elif "darwin" in system or "mac" in system:
# else:
#     print("抱歉，暂不支持 Mac OS 系统")
#     raise SystemError("暂不支持 Mac OS 系统")
    SystemType = "Mac"
else:
    print("未知系统！")
    raise SystemError("暂不支持该系统")
# 初始化日志

try:
    os.mkdir("log")
except FileExistsError:
    pass

# （已修复）删除了程序正在使用的日志文件 #
# 修复方法：将这一段放到生成日志之前运行
# 删除没有内容的日志文件
ct = len(os.listdir("log"))
for lf in os.listdir("log"):
    if not os.path.getsize(f"log/{lf}") > 0:
        os.remove(f"log/{lf}")
        logging.info(f"删除无内容的日志文件：{lf}")
        continue
    elif ct == 0:
        break
    else:
        ct = ct - 1
        continue

# 删除无意义的日志文件（小于等于 3 行)
ct = len(os.listdir("log"))
for lf in os.listdir("log"):
    with open(f"log/{lf}", "r", encoding="utf-8") as f:
        lines = f.readlines()
        if len(lines) <= 3:
            os.remove(f"log/{lf}")
            logging.info(f"删除无意义的日志文件：{lf}")
            continue
        elif ct == 0:
            break
        else:
            continue

LOGFORMAT = "[%(pathname)s | %(funcName)s | %(process)d | %(lineno)d] [%(levelname)s %(asctime)s] %(message)s"
DATEFORMAT = "%Y/%m/%d %H:%M:%S"
LOGFILEFORMAT = "%Y_%m_%d-%H-%M-%S"
# [C:/hello/main.py | getServerjar | 8] [WARNING 2023/07/24 11:11:11] text here...
LOGFILENAME = f"{time.strftime(LOGFILEFORMAT)}.log"

with open(file=f"log/{LOGFILENAME}", mode="x", encoding="utf-8") as f:
    pass

logging.basicConfig(
    level=logging.NOTSET,
    format=LOGFORMAT,
    datefmt=DATEFORMAT,
    filename=f"log/{LOGFILENAME}",
    filemode="a"
)
logging.info(f"当前系统：{SystemType}")
logging.info("日志模块 初始化完成")
# 初始化配置
config = configparser.ConfigParser()

if not os.path.exists("config.ini"):
    config["Server"] = {
        'ServerVersion': 'auto',
        'type': 'vanilla',
        'useRelease': True,
        'dev': False,
        'done': False
    }

    with open(file='config.ini', mode='w', encoding="utf-8") as f:
        config.write(f)
    CFGREADSOON = True
else:
    # config read at soon
    CFGREADSOON = True

# 初始化 rich
console = Console()
# 读取版本信息
try:
    os.remove("version_manifest_v2.json")
    os.remove("version_manifest.json")
except FileNotFoundError:
    logging.debug("未检测到 version_manifest.json 文件，继续运行")
else:
    logging.info("检测到 version_manifest.json 文件，删除以避免重复")
logging.info("开始下载 version_manifest json")
try:
    wget.download('https://piston-meta.mojang.com/mc/game/version_manifest.json')
    wget.download(
    'https://piston-meta.mojang.com/mc/game/version_manifest_v2.json')
except socket.gaierror:
    logging.warning("无法连接到 piston-meta.mojang.com")
    console.print("[yellow]无法连接到 piston-meta.mojang.com[/]")
    console.print("请检查您的网络设置")
    exit(1)
except urllib.error.URLError:
    logging.warning("无法连接到 piston-meta.mojang.com")
    console.print("[yellow]无法连接到 piston-meta.mojang.com[/]")
    console.print("请检查您的网络设置")
    exit(1)
print("\n", end="")
with open("version_manifest_v2.json", "r", encoding="utf-8") as f:
    content = json.load(f)
latest_release = content['latest']['release']
latest_snapshot = content['latest']['snapshot']
# "latest": {
#         "release": "1.20.1",
#         "snapshot": "1.20.1"
#     },
# print(platform.uname())
x = len(content['versions'])
i = 0
v = []
vx = []
while i < len(content['versions']):
    v.append(content['versions'][i])
    vx.append(content['versions'][i]['id'])
    i += 1
logging.debug(f"共有 {x} 个版本")

if CFGREADSOON:
    with open(file='config.ini', mode="r", encoding="utf-8") as f:
        config = configparser.ConfigParser()
        config.read_file(f)
        type = config["Server"]["type"]
        use_release = config["Server"]["useRelease"]
        if config["Server"]["ServerVersion"] == 'auto':
            if use_release == 'True':
                ServerVersion = latest_release
            else:
                ServerVersion = latest_snapshot
        else:
            ServerVersion = config["Server"]["ServerVersion"]
        logging.info(f"已检测到所需版本 {ServerVersion}")
        ic = 0
        for nm in vx:
            if nm == ServerVersion:
                logging.debug(f"该版本存在")
                ik = 0
                break
            elif ic == len(vx) - 1:
                logging.warning(f"该版本不存在")
                console.print("[yellow]该版本不存在。[/]")
                console.print("请输入在 version_manifest.json 中描述的版本。")
                console.print("例如，不要输入 pre-1.6，而输入 1.0。")
                ik = 1
                break
            ic = ic + 1
        if ik == 1:
            logging.info(f"使用最新版本")
            if use_release == 'True':
                ServerVersion = latest_release
            else:
                ServerVersion = latest_snapshot
        elif ik == 0:
            logging.info("使用当前版本")
        else:
            logging.critical("发生未知错误")
            raise Exception("发生未知错误: 变量 ik 非正常值")
        logging.info(f"开始下载版本")
        url = content['versions'][vx.index(ServerVersion)]['url']
        try:
            os.remove(f"{ServerVersion}.json")
        except FileNotFoundError:
            logging.debug(f"未检测到 {ServerVersion}.json 文件，继续运行")
        else:
            logging.info(f"检测到 {ServerVersion}.json 文件，删除以避免重复")
        logging.info(f"开始下载版本信息文件 {ServerVersion}.json")
        wget.download(url)
        print("\n", end="")
        with open(f"{ServerVersion}.json", "r", encoding="utf-8") as f:
            content = json.load(f)
        logging.info(f"版本信息文件 {ServerVersion}.json 下载完成")
        logging.debug(f"开始读取")
        # print(content)
        try:
            DownloadSHA1 = content['downloads']['server']['sha1']
            DownloadUrl = content['downloads']['server']['url']
        except KeyError:
            logging.error(f"版本核心 {ServerVersion} 下载失败")
            logging.critical(f"版本过旧，缺少下载信息。")
            console.print("[red]版本过旧，缺少下载信息。[/]")
            exit(1)
        try:
            os.remove("server.jar")
        except FileNotFoundError:
            logging.debug("未检测到 server.jar 文件，继续运行")
        else:
            logging.info("检测到 server.jar 文件，删除以避免重复")
        wget.download(DownloadUrl)
        print("\n", end="")

        def getSha1(filename):  # 计算sha1
            sha1Obj = hashlib.sha1()
            with open(filename, 'rb') as f:
                sha1Obj.update(f.read())
            return sha1Obj.hexdigest()
        sha1 = getSha1("server.jar")
        if sha1 != DownloadSHA1:
            logging.error(f"版本核心 {ServerVersion} 下载失败")
            logging.critical(f"sha1 校验失败。")
            raise Exception("SHA1 校验错误！")
            # 下载 Java
            logging.info("检测用户是否安装了 Java")
            
#             if SystemType == "Linux":
#                 # Linux
#                 # 例：1.19.2 -> 1192
#                 svl = ServerVersion.split(".")
#                 i = len(svl)
#                 k = ""
#                 for s in svl:
#                     if i > 0:
#                         k = k + s
#                     else:
#                         break
#                     i = i - 1
#                 ServerVersionLX = k
#                 os.system("chmod +x server.jar")
#                 os.system(f"mkdir ./server")
#                 os.system(f"mkdir ./server/{ServerVersionLX}")
#                 os.system(f"mv server.jar ./server/{ServerVersionLX}/server.jar")
#             elif SystemType == "Windows":
#                 # Windows
#                 os.system("mkdir ./server")
#                 os.system(f"mkdir ./server/{ServerVersion}")
