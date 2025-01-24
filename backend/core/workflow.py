from backend.core import data_process, data_crawl

def workflow(keyword: str, pages: int, file_path: str):
    print('开始爬取数据')
    data_crawl.crawl_data(keyword, pages, file_path)
    print('开始处理数据')
    data_process.clean_data(file_path)
    data_process.sort_data(file_path)