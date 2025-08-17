# 集思录可转债爬虫

这是一个用于爬取集思录可转债详情页的爬虫工具。该工具可以批量爬取多个可转债的详细信息，并将数据保存为JSON和CSV格式。

## 功能特点

- 支持批量爬取多个可转债详情页
- 自动解析页面中的关键数据
- 数据保存为JSON和CSV格式
- 支持命令行参数
- 内置反爬措施（随机延时）

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 命令行方式

```bash
# 爬取单个可转债
python jisilu_crawler.py 113046

# 爬取多个可转债
python jisilu_crawler.py 113046 113566 113633

# 指定输出目录
python jisilu_crawler.py 113046 113566 --output ./output_data
```

### 作为模块导入

```python
from jisilu_crawler import JisiluCrawler

# 创建爬虫实例
crawler = JisiluCrawler(output_dir='./data')

# 爬取多个可转债
bond_codes = ['113046', '113566', '113633']
results = crawler.crawl_bonds(bond_codes)

# 保存合并数据
crawler.save_all_bonds_csv(results)
```

## 数据格式

爬虫会提取可转债详情页中的关键数据，包括但不限于：

- 可转债名称和代码
- 正股名称和代码
- 转债价格和转股价值
- 溢价率和到期收益率
- 转股起始日和到期日
- 回售条款和强赎条款

## 示例

项目包含一个示例脚本 `example.py`，展示了如何使用该爬虫：

```bash
python example.py
```

## 注意事项

- 请合理控制爬取频率，避免对目标网站造成过大压力
- 爬取的数据仅用于个人研究，请勿用于商业用途
- 网站结构可能发生变化，可能需要更新爬虫代码