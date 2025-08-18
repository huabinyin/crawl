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
import re
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
    
    def get_bond_info(self, bond_code, use_local_file=False):
        """获取单个可转债信息"""
        url = f"{self.base_url}{bond_code}"
        
        try:
            if use_local_file:
                # 从本地文件加载HTML
                debug_path = os.path.join(self.output_dir, f"{bond_code}_debug.html")
                if os.path.exists(debug_path):
                    print(f"从本地文件加载HTML: {debug_path}")
                    with open(debug_path, 'r', encoding='utf-8') as f:
                        html_content = f.read()
                else:
                    print(f"本地文件不存在: {debug_path}")
                    return None
            else:
                # 从网站爬取HTML
                print(f"正在爬取: {url}")
                response = requests.get(url, headers=self.headers, timeout=10)
                response.raise_for_status()  # 如果响应状态码不是200，将引发HTTPError异常
                html_content = response.text
                
                # 保存HTML内容用于调试
                debug_path = os.path.join(self.output_dir, f"{bond_code}_debug.html")
                with open(debug_path, 'w', encoding='utf-8') as f:
                    f.write(html_content)
                print(f"已保存HTML内容到 {debug_path} 用于调试")
            
            # 解析HTML
            soup = BeautifulSoup(html_content, 'lxml')
            
            # 提取可转债名称和代码 - 从title标签或表格中提取
            bond_name = "未知"
            # 从title标签提取
            title_elem = soup.select_one('title')
            if title_elem:
                title_text = title_elem.text.strip()
                # 通常格式为"科沃转债 - 113633 - 集思录"
                if ' - ' in title_text:
                    bond_name = title_text.split(' - ')[0].strip()
                    print(f"从title标签找到可转债名称: {bond_name}")
            
            # 如果title中没找到，尝试从表格中提取
            if bond_name == "未知":
                for table in soup.select('table'):
                    for row in table.select('tr'):
                        cells = row.select('td')
                        if len(cells) >= 2:
                            if cells[0].text.strip() == "名称":
                                bond_name = cells[1].text.strip()
                                print(f"从表格中找到可转债名称: {bond_name}")
                                break
            
            # 提取正股名称和代码
            stock_name = "未知"
            # 从表格头部提取正股名称
            stock_info = soup.select_one('.stock_nm')
            if stock_info:
                stock_link = stock_info.select_one('a')
                if stock_link:
                    # 提取完整的正股名称和代码，例如："金田股份 601609"
                    stock_name = stock_link.text.strip()
                    print(f"找到正股名称: {stock_name}")
            
            # 提取行业信息
            industry = "未知"
            # 从表格头部提取行业信息
            industry_info = soup.select_one('.stock_indu')
            if industry_info:
                # 优先尝试获取新版行业链接
                industry_link = industry_info.select_one('a#industry_new')
                if industry_link:
                    industry = industry_link.text.strip()
                    print(f"找到行业信息: {industry}")
                else:
                    # 尝试获取旧版行业链接
                    industry_link = industry_info.select_one('a#industry_old')
                    if industry_link:
                        industry = industry_link.text.strip()
                        print(f"找到行业信息: {industry}")

            
            # 提取所有数据项
            data_items = {}
            
            # 提取价格、溢价率等基本信息
            # 从表格中提取价格
            price = "未知"
            price_cell = soup.select_one('td.jisilu_subtitle span[style="color:red"]')
            if price_cell:
                price = price_cell.text.strip()
                print(f"从表格中找到价格: {price}")
            
            # 提取其他基本信息 - 尝试多种选择器
            selectors_pairs = [
                ('div.item-value', 'div.item-label'),
                ('.item-value', '.item-label'),
                ('.cb-item-value', '.cb-item-label'),
                ('.data-item-value', '.data-item-label'),
                ('.value', '.label'),
                ('td.value', 'td.label'),
                ('span.value', 'span.label')
            ]
            
            for value_selector, label_selector in selectors_pairs:
                price_items = soup.select(value_selector)
                price_labels = soup.select(label_selector)
                
                if price_items and price_labels:
                    print(f"找到数据项: {len(price_labels)} 个 (使用选择器: {label_selector}, {value_selector})")
                    for i in range(len(price_labels)):
                        if i < len(price_items):
                            label = price_labels[i].text.strip()
                            value = price_items[i].text.strip()
                            data_items[label] = value
            
            # 提取日期、转股价等详细信息 - 尝试多种选择器
            detail_selectors_pairs = [
                ('div.cb-value', 'div.cb-label'),
                ('.cb-value', '.cb-label'),
                ('.detail-value', '.detail-label'),
                ('.info-value', '.info-label'),
                ('td.detail-value', 'td.detail-label'),
                ('span.detail-value', 'span.detail-label')
            ]
            
            for value_selector, label_selector in detail_selectors_pairs:
                detail_items = soup.select(value_selector)
                detail_labels = soup.select(label_selector)
                
                if detail_items and detail_labels:
                    print(f"找到详细信息: {len(detail_labels)} 个 (使用选择器: {label_selector}, {value_selector})")
                    for i in range(len(detail_labels)):
                        if i < len(detail_items):
                            label = detail_labels[i].text.strip()
                            value = detail_items[i].text.strip()
                            data_items[label] = value
            
            # 尝试提取表格数据
            tables = soup.select('table')
            for table_idx, table in enumerate(tables):
                rows = table.select('tr')
                for row in rows:
                    cells = row.select('td, th')
                    if len(cells) >= 2:  # 至少有两列：标签和值
                        label = cells[0].text.strip()
                        value = cells[1].text.strip()
                        if label and value:
                            # 将表格标题也翻译成中文
                            translated_label = f"表格{table_idx+1}-{label}"
                            data_items[translated_label] = value
            
            # 提取概念标签
            tags = []
            # 根据HTML结构，概念标签在class为concept的div下的class为item的div中
            concept_div = soup.select_one('div.concept')
            if concept_div:
                tag_items = concept_div.select('div.item a')
                for tag_item in tag_items:
                    tag_text = tag_item.text.strip()
                    if tag_text:
                        tags.append(tag_text)
                print(f"找到概念标签: {tags}")
            
            # 提取价格、税前收益率、溢价率等关键数据
            price = "未知"
            ytm_rt = "未知"  # 税前收益率
            premium_rt = "未知"  # 溢价率
            
            # 从表格中提取这些数据
            for table in soup.select('table.jisilu_tcdata'):
                for row in table.select('tr'):
                    cells = row.select('td.jisilu_subtitle')
                    for cell in cells:
                        text = cell.text.strip()
                        if "价格" in text:
                            price_span = cell.select_one('span[style="color:red"]')
                            if price_span:
                                price = price_span.text.strip()
                                print(f"找到价格: {price}")
                        elif "到期税前收益" in text:
                            ytm_rt = text.replace("到期税前收益", "").strip()
                            print(f"找到税前收益率: {ytm_rt}")
                        elif "溢价率" in text:
                            premium_rt = text.replace("溢价率", "").strip()
                            print(f"找到溢价率: {premium_rt}")
            
            # 移除之前的数据项提取逻辑，因为它会覆盖已经找到的正确值
            result = {
                "bond_code": bond_code,
                "bond_name": bond_name,
                "stock_name": stock_name,
                "industry": industry,
                "price": price,
                "ytm_rt": ytm_rt,
                "premium_rt": premium_rt,
                "concept_tags": tags,
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
    
    def crawl_bonds(self, bond_codes, use_local_file=False):
        """批量爬取多个可转债信息"""
        results = []
        
        for bond_code in bond_codes:
            try:
                bond_info = self.get_bond_info(bond_code, use_local_file)
                if bond_info:
                    results.append(bond_info)
                    
                    # 保存单个可转债数据
                    self.save_bond_data(bond_info, bond_code)
                    
                    # 随机延时，避免被反爬
                    time.sleep(random.uniform(1, 3))
            except Exception as e:
                print(f"处理 {bond_code} 时发生错误: {e}")
        
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
            flat_data = {"转债代码": bond_data["bond_code"], 
                         "转债名称": bond_data["bond_name"],
                         "正股名称": bond_data["stock_name"],
                         "行业": bond_data["industry"],
                         "价格": bond_data["price"],
                         "税前收益率": bond_data["ytm_rt"],
                         "溢价率": bond_data["premium_rt"],
                         "概念标签": ",".join(bond_data["concept_tags"]),
                         "爬取时间": bond_data["crawl_time"]}
            
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
                flat_data = {"转债代码": bond_data["bond_code"], 
                             "转债名称": bond_data["bond_name"],
                             "正股名称": bond_data["stock_name"],
                             "行业": bond_data["industry"],
                             "价格": bond_data["price"],
                             "税前收益率": bond_data["ytm_rt"],
                             "溢价率": bond_data["premium_rt"],
                             "概念标签": ",".join(bond_data["concept_tags"]),
                             "爬取时间": bond_data["crawl_time"]}
                
                # 添加data中的所有键值对
                for k, v in bond_data["data"].items():
                    flat_data[k] = v
                    all_fields.add(k)
                
                flat_data_list.append(flat_data)
            
            # 确保所有字段都存在于每个记录中
            fieldnames = ["转债代码", "转债名称", "正股名称", "行业", "价格", "税前收益率", "溢价率", "概念标签", "爬取时间"] + list(all_fields)
            
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
    parser.add_argument('--local', '-l', action='store_true', help='使用本地HTML文件而不是从网络爬取')
    
    args = parser.parse_args()
    
    # 创建爬虫实例
    crawler = JisiluCrawler(output_dir=args.output)
    
    # 开始爬取
    print(f"开始爬取 {len(args.bond_codes)} 个可转债数据...")
    results = crawler.crawl_bonds(args.bond_codes, use_local_file=args.local)
    
    # 保存所有数据到一个CSV文件
    if results:
        all_csv_path = crawler.save_all_bonds_csv(results)
        if all_csv_path:
            print(f"所有数据已合并保存到: {all_csv_path}")
    
    print("爬取完成!")


if __name__ == '__main__':
    main()