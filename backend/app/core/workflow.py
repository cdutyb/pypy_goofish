import os

from backend.app.core import data_process, data_crawl

def workflow(keyword: str, pages: int, file_path: str):
    # data_dir = os.path.join("..", "data")  # 测试时使用
    # if not os.path.exists(data_dir):
    #     os.makedirs(data_dir, exist_ok=True)

    print('开始爬取数据...')
    data_crawl.crawl_data(keyword, pages, file_path)
    print('开始处理数据...')
    data_process.clean_data(file_path)
    print('开始排序数据...')
    data_process.sort_data(file_path)
