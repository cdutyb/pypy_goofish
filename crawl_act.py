import requests
import time
import json
import csv
import re
import os
import hashlib
from selenium import webdriver
from selenium.webdriver.edge.service import Service

# 请求参数和头部
cookies = {
    'cna': 'odEHIBj1MFsCAXSpBFre+QLT',
    't': '1ea28772586b53a1f8fbb1508f336f05',
    'isg': 'BKioB87bW8tq9ndP-7hzIhAteZa60Qzb8WgWDWLZyCMWvUgnCuL_ayr0tVVNjcSz',
    'mtop_partitioned_detect': '1',
    '_m_h5_tk': '',
    '_m_h5_tk_enc': '',
    'xlly_s': '1',
    '_samesite_flag_': 'true',
    '_tb_token_': 'f88bea77a0780',
    'cookie2': '176b3878b27e725c86dc45d731434373',
    'tfstk': 'gFGjarAOWijjLoKiEmYzA1RmUyFshURF5Nat-VCVWSFAXG3L4mr4gFA_Xmqrgou4MlCsbVlqbfgG1P3tjEqwoLumo5V9YHP6Tq0cSAg2J3P9W4Fa5g0ZhMgmo5blzGpEeqj6MX-U65nTw8UgR5BTXoL7wP4L6seOMTI8quET6oCAwQUaklCTDlLSyu4_6lnTHUN-BnK7rKZxlETv5RVP653YV1CtMC2YA_ZzrzcWY-rKkj1O6eUbhk3YVHqH4Ke-SRGGS1wZkvmgJmIvflcSyjHKv3W4Dvas8Aip7t4zCjV7XjdhRuhj5bwmUiBYRSZbpjef8e00BYG7gjKGK4u7DJNrULx4QSijKk2vE3msPootG8IX4lkEzjeSv35SjRMtg7hv2BsyV6rCnDX1PJf_Pk8WPOXgtc5mJbd7aLwYrzlePUsfI-UuP78WPOXgHz4zUUT5cOf..',
}

headers = {
    'accept': 'application/json',
    'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6',
    'cache-control': 'no-cache',
    'origin': 'https://www.goofish.com',
    'referer': 'https://www.goofish.com/',
    'sec-ch-ua': '"Microsoft Edge";v="131", "Chromium";v="131", "Not_A Brand";v="24"',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36 Edg/131.0.0.0',
}

params = {
    'jsv': '2.7.2',
    'appKey': '34839810',
    't': '1737180672460',
    'sign': 'f16d2175690afdd972c03c089faff42a',
    'v': '1.0',
    'type': 'originaljson',
    'accountSite': 'xianyu',
    'dataType': 'json',
    'timeout': '20000',
    'api': 'mtop.taobao.idlemtopsearch.pc.search',
    'sessionOption': 'AutoLoginOnly',
    'spm_cnt': 'a21ybx.search.0.0',
    'spm_pre': 'a21ybx.home.searchInput.0'
    # 'log_id': '4c053da6ZAW7yN',
}

data = {
    'data': '{"pageNumber":0,"keyword":"无人机","fromFilter":false,"rowsPerPage":30,"sortValue":"","sortField":"","customDistance":"","gps":"","propValueStr":{"searchFilter":""},"customGps":"","searchReqFromPage":"pcSearch","extraFilterValue":"{}","userPositionJson":"{}"}',
}

pattern = re.compile(r'(\d+)人想要')


# MD5签名函数
def md5(key):
    md5_obj = hashlib.md5()
    md5_obj.update(key.encode('utf-8'))
    return md5_obj.hexdigest()


def append_unique_data_to_csv(new_items, keyword):
    # 定义 CSV 文件路径
    csv_file = f'data/{keyword}_items.csv'

    # 利用商品链接的唯一性，如果文件存在，读取已有数据中的商品链接，避免重复
    existing_links = set()
    if os.path.exists(csv_file):
        with open(csv_file, 'r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                existing_links.add(row['商品链接'])

    # 新数据去重：只添加不重复的商品
    new_items_filtered = [item for item in new_items if item['商品链接'] not in existing_links]

    if not new_items_filtered:
        print("没有新的商品数据，跳过保存")
        return
    else:
        print(f"正在保存 {len(new_items_filtered)} 个新的商品数据到 {csv_file}")

    # 以追加模式打开文件并写入新数据
    with open(csv_file, 'a', newline='', encoding='utf-8-sig') as file:
        fieldnames = ['商品名称', '价格', '商品链接', '卖家地址', '卖家ID', '商品标签', '想要人数', '图片链接',
                      '是否包邮', '评价数', '好评率']
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        # 只在文件为空时写入表头
        if file.tell() == 0:  # 如果文件为空，写入表头
            writer.writeheader()

        # 写入新的、不重复的数据
        for item in new_items_filtered:
            writer.writerow(item)

    print(f"数据爬取完成并追加到 {csv_file}")


# 爬取数据
def crawl_data(keyword, pages):
    items_data = []
    original_data = data['data']

    # 设置 Edge 浏览器驱动路径
    service = Service('edgedriver_win64/msedgedriver.exe')
    driver = webdriver.Edge(service=service)
    driver.get('https://www.goofish.com/')
    time.sleep(2)
    cookiess = driver.get_cookies()  # 获取有效的 cookie
    driver.quit()
    # 设置新的 cookie，获取有效令牌
    for cookie in cookiess:
        name = cookie.get('name')
        if name in ('_m_h5_tk', '_m_h5_tk_enc'):
            cookies[name] = cookie.get('value')

    for page in range(1, pages + 1):  # 循环页数，获取每一页的数据
        time.sleep(1)
        data['data'] = original_data.replace('无人机',keyword).replace('0', str(page), 1)  # 根据用户输入替换关键词和页数
        j = round(time.time() * 1000)
        h = params['appKey']
        key = cookies['_m_h5_tk'].split("_")[0] + "&" + str(j) + "&" + h + "&" + data['data']
        sign = md5(key)  # 获取签名
        params['sign'] = sign
        params['t'] = str(j)

        response = requests.post('https://h5api.m.goofish.com/h5/mtop.taobao.idlemtopsearch.pc.search/1.0/', params=params, cookies=cookies, headers=headers, data=data)
        # print(response.status_code)
        resultList = response.json()['data']['resultList']  # 获取结果列表
        # 打印商品数量
        print(f"正在获取第 {page} 页的商品数据...")
        print(f"获取到 {len(resultList)} 个商品数据")
        for result in resultList:
            # 获取商品链接
            categoryId = result['data']['item']['main']['clickParam']['args'].get('cCatId', '未知分类')
            item_id = result['data']['item']['main']['clickParam']['args'].get('item_id', '未知ID')
            link = f'https://www.goofish.com/item?id={item_id}&categoryId={categoryId}'

            # 获取商品名称
            title = result['data']['item']['main']['exContent'].get('title', '未知标题')

            # 获取商品价格
            price = result['data']['item']['main']['clickParam']['args'].get('price', '未知价格')

            # 卖家地址
            seller_area = result['data']['item']['main']['exContent'].get('area', '未知地区')

            # 卖家名称
            seller_ID = result['data']['item']['main']['exContent'].get('userNickName', '未知卖家')

            # 商品标签
            tags_raw = result['data']['item']['main']['clickParam']['args'].get('serviceUtParams', '[]')

            try:
                tags_list = json.loads(tags_raw)
                tags = [tag['args']['content'] for tag in tags_list]
            except json.JSONDecodeError:
                tags = []

            # 想要此商品的人数
            want_num = ''.join(pattern.findall(tags_raw))

            # 商品图片
            img_url = result['data']['item']['main']['exContent'].get('picUrl', '未知图片')

            # 是否包邮
            shipping_value = 1 if tags and tags[-1] == "freeShippingIcon" else 0

            # 评价人数和好评率
            tagList = result['data']['item']['main']['exContent']['userFishShopLabel']['tagList']
            rate_num = tagList[0]['data'].get('content', '未知条评价').replace('条评价', '')
            rate_percent = tagList[1]['data'].get('content', '未知好评率').replace('好评率', '')

            # 收集数据
            item = {
                '商品名称': title,
                '价格': price,
                '商品链接': link,
                '卖家地址': seller_area,
                '卖家ID': seller_ID,
                '商品标签': ', '.join(tags),
                '想要人数': want_num,
                '图片链接': img_url,
                '是否包邮': shipping_value,
                '评价数': rate_num,
                '好评率': rate_percent,
            }
            items_data.append(item)

    append_unique_data_to_csv(items_data, keyword)
    print(f"数据爬取完成并保存为 {keyword}_items.csv")