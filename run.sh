#!/bin/bash

# 集思录可转债爬虫运行脚本

# 检查是否安装了依赖
if [ ! -f "$(which pip)" ]; then
    echo "错误: 请先安装Python和pip"
    exit 1
fi

# 安装依赖
echo "正在检查并安装依赖..."
pip install -r requirements.txt

# 检查参数
if [ $# -eq 0 ]; then
    echo "用法: $0 <可转债代码1> [可转债代码2] [可转债代码3] ..."
    echo "示例: $0 113046 113566"
    exit 1
fi

# 创建数据目录
mkdir -p ./data

# 运行爬虫
echo "开始爬取可转债数据..."
python jisilu_crawler.py "$@"

echo "爬取完成!"