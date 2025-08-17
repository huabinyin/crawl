#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
使用示例：演示如何使用集思录可转债爬虫
"""

from jisilu_crawler import JisiluCrawler


def main():
    # 创建爬虫实例，指定输出目录
    crawler = JisiluCrawler(output_dir='./data')
    
    # 定义要爬取的可转债代码列表
    bond_codes = ['113046', '113566', '113633']
    
    print(f"开始爬取 {len(bond_codes)} 个可转债数据...")
    
    # 批量爬取可转债数据
    results = crawler.crawl_bonds(bond_codes)
    
    # 将所有数据合并保存为一个CSV文件
    if results:
        all_csv_path = crawler.save_all_bonds_csv(results)
        if all_csv_path:
            print(f"所有数据已合并保存到: {all_csv_path}")
    
    print("爬取完成!")


if __name__ == '__main__':
    main()