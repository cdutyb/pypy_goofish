from flask import Flask, render_template, request, jsonify
import crawl_act as cra
import cleaner as cle
import os
import pandas as pd

app = Flask(__name__)

# 创建数据存储目录
data_dir = 'data'
output_dir = 'cleaned_data'
if not os.path.exists(data_dir):
    os.makedirs(data_dir)
if not os.path.exists(output_dir):
    os.makedirs(output_dir)

all_data = []


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/crawl', methods=['POST'])
def crawl():
    global all_data
    keyword = request.json.get('keyword')
    pages = int(request.json.get('pages'))

    # 清空数据
    all_data = []

    # 执行爬取
    cra.crawl_data(keyword, pages)

    # 清理数据并保存
    csv_file = f'{keyword}_items.csv'
    file_path = os.path.join(data_dir, csv_file)
    cle.clean_data(file_path, output_dir)

    # 读取清理后的数据
    cleaned_file_path = os.path.join(output_dir, f'{keyword}_cleaned_items.csv')
    df = pd.read_csv(cleaned_file_path)

    # 确保字段的存在
    expected_columns = [
        "商品名称", "价格", "商品链接", "卖家地址", "卖家ID",
        "商品标签", "想要人数", "图片链接", "是否包邮", "评价数", "好评率"
    ]
    df = df[expected_columns]

    # 将数据加入到全局数据列表中
    all_data.extend(df.to_dict(orient='records'))

    # 返回全部数据的分页信息
    return jsonify({
        'total_pages': (len(all_data) // 30) + (1 if len(all_data) % 30 > 0 else 0),
        'data': all_data[:30]  # 默认返回第一页的数据
    })


@app.route('/page', methods=['GET'])
def page():
    page_num = int(request.args.get('page', 1))  # 获取请求的页码
    start_index = (page_num - 1) * 30
    end_index = start_index + 30
    data_page = all_data[start_index:end_index]
    return jsonify(data_page)


if __name__ == '__main__':
    app.run(debug=True)
