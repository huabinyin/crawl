#!/usr/bin/env python
# -*- coding: utf-8 -*-

import requests
import argparse
import time
import random
from bs4 import BeautifulSoup
import os
import json
import csv
from datetime import datetime


class JisiluCrawler:
    """集思录可转债爬虫"""
    
    def __init__(self, output_dir='./data'):
        self.base_url = 'https://www.jisilu.cn/data/convert_bond_detail/'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        }
        self.output_dir = output_dir
        
        # 创建输出目录
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
    
    def get_bond_info(self, bond_code):
        """获取单个可转债信息"""
        url = f"{self.base_url}{bond_code}"
        print(f"正在爬取: {url}")
        
        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
            
            # 解析HTML
            soup = BeautifulSoup(response.text, 'lxml')
            
            # 提取可转债名称和代码
            bond_name_elem = soup.select_one('div.bond-name')
            bond_name = bond_name_elem.text.strip() if bond_name_elem else "未知"
            
            # 提取正股名称和代码
            stock_name_elem = soup.select_one('div.stock-name')
            stock_name = stock_name_elem.text.strip() if stock_name_elem else "未知"
            
            # 提取所有数据项
            data_items = {}
            
            # 提取价格、溢价率等基本信息
            price_items = soup.select('div.item-value')
            price_labels = soup.select('div.item-label')
            
            for i in range(len(price_labels)):
                if i < len(price_items):
                    label = price_labels[i].text.strip()
                    value = price_items[i].text.strip()
                    data_items[label] = value
            
            # 提取日期、转股价等详细信息
            detail_items = soup.select('div.cb-value')
            detail_labels = soup.select('div.cb-label')
            
            for i in range(len(detail_labels)):
                if i < len(detail_items):
                    label = detail_labels[i].text.strip()
                    value = detail_items[i].text.strip()
                    data_items[label] = value
            
            # 组合结果
            result = {
                "bond_code": bond_code,
                "bond_name": bond_name,
                "stock_name": stock_name,
                "crawl_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "data": data_items
            }
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"爬取 {bond_code} 时发生错误: {e}")
            return None
        except Exception as e:
            print(f"处理 {bond_code} 数据时发生错误: {e}")
            return None
    
    def crawl_bonds(self, bond_codes):
        """批量爬取多个可转债信息"""
        results = []
        
        for bond_code in bond_codes:
            bond_info = self.get_bond_info(bond_code)
            if bond_info:
                results.append(bond_info)
                
                # 保存单个可转债数据
                self.save_bond_data(bond_info, bond_code)
                
                # 随机延时，避免被反爬
                time.sleep(random.uniform(1, 3))
        
        return results
    
    def save_bond_data(self, bond_data, bond_code):
        """保存可转债数据到文件"""
        if not bond_data:
            return
        
        # 保存为JSON
        json_path = os.path.join(self.output_dir, f"{bond_code}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(bond_data, f, ensure_ascii=False, indent=2)
        
        print(f"已保存 {bond_code} 数据到 {json_path}")
        
        # 保存为CSV
        try:
            # 将嵌套的data字典展平
            flat_data = {"bond_code": bond_data["bond_code"], 
                         "bond_name": bond_data["bond_name"],
                         "stock_name": bond_data["stock_name"],
                         "crawl_time": bond_data["crawl_time"]}
            
            # 添加data中的所有键值对
            for k, v in bond_data["data"].items():
                flat_data[k] = v
            
            # 保存为CSV
            csv_path = os.path.join(self.output_dir, f"{bond_code}.csv")
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=flat_data.keys())
                writer.writeheader()
                writer.writerow(flat_data)
            print(f"已保存 {bond_code} 数据到 {csv_path}")
            
        except Exception as e:
            print(f"保存 {bond_code} 为CSV时发生错误: {e}")
    
    def save_all_bonds_csv(self, all_bonds_data):
        """将所有可转债数据合并保存为一个CSV文件"""
        if not all_bonds_data:
            return
        
        try:
            # 准备展平的数据列表
            flat_data_list = []
            all_fields = set()
            
            for bond_data in all_bonds_data:
                # 将嵌套的data字典展平
                flat_data = {"bond_code": bond_data["bond_code"], 
                             "bond_name": bond_data["bond_name"],
                             "stock_name": bond_data["stock_name"],
                             "crawl_time": bond_data["crawl_time"]}
                
                # 添加data中的所有键值对
                for k, v in bond_data["data"].items():
                    flat_data[k] = v
                    all_fields.add(k)
                
                flat_data_list.append(flat_data)
            
            # 确保所有字段都存在于每个记录中
            fieldnames = ["bond_code", "bond_name", "stock_name", "crawl_time"] + list(all_fields)
            
            # 生成带时间戳的文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            csv_path = os.path.join(self.output_dir, f"all_bonds_{timestamp}.csv")
            
            # 保存为CSV
            with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                for data in flat_data_list:
                    # 确保所有字段都存在
                    for field in fieldnames:
                        if field not in data:
                            data[field] = ""
                    writer.writerow(data)
            
            print(f"已保存所有可转债数据到 {csv_path}")
            return csv_path
            
        except Exception as e:
            print(f"保存所有可转债数据为CSV时发生错误: {e}")
            return None


def main():
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='集思录可转债爬虫')
    parser.add_argument('bond_codes', nargs='+', help='可转债代码列表，如 113046 113566')
    parser.add_argument('--output', '-o', default='./data', help='输出目录路径')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = JisiluCrawler(output_dir=args.output)
    
    # 开始爬取
    print(f"开始爬取 {len(args.bond_codes)} 个可转债数据...")
    results = crawler.crawl_bonds(args.bond_codes)
    
    # 保存所有数据到一个CSV文件
    if results:
        all_csv_path = crawler.save_all_bonds_csv(results)
        if all_csv_path:
            print(f"所有数据已合并保存到: {all_csv_path}")
    
    print("爬取完成!")


if __name__ == '__main__':
    main()