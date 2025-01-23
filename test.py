import crawl_act as cra
import cleaner as cle
import os


# 用户输入商品名称和页数
keyword = input("请输入要爬取的商品名称: ")  # 获取用户输入的商品名称
pages = int(input("请输入要爬取的页数: "))  # 获取用户输入的页数

# 爬取数据并保存到CSV文件
cra.crawl_data(keyword, pages)

# 清理数据并保存到CSV文件
data_dir = 'data'
output_dir = 'cleaned_data'
csv_file = f'{keyword}_items.csv'
file_path = os.path.join(data_dir, csv_file)
# 创建新目录，如果不存在
if not os.path.exists(output_dir):
    os.makedirs(output_dir)
if not os.path.exists(output_dir):
    os.makedirs(data_dir)

cle.clean_data(file_path, output_dir)
