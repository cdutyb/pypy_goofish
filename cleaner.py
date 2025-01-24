import pandas as pd
import os


# 定义数据清洗函数
def clean_data(file_path, output_dir):
    item_name = file_path.split('\\')[-1].split('_')[0]  # 从文件路径提取文件名
    print(f"正在处理：{item_name}")

    # 加载数据
    df = pd.read_csv(file_path)

    # 检查并转换数据类型
    df['好评率'] = df['好评率'].str.replace('%', '')  # 去掉百分号
    df['价格'] = pd.to_numeric(df['价格'], errors='coerce')  # 将价格列转为数值型
    df['评价数'] = pd.to_numeric(df['评价数'], errors='coerce')
    df['好评率'] = pd.to_numeric(df['好评率'], errors='coerce')
    df['想要人数'] = pd.to_numeric(df['想要人数'], errors='coerce')

    df['是否包邮'] = df['是否包邮'].astype(int)
    df['商品名称'] = df['商品名称'].astype(str)
    df['商品链接'] = df['商品链接'].astype(str)
    df['卖家地址'] = df['卖家地址'].astype(str)
    df['卖家ID'] = df['卖家ID'].astype(str)
    df['商品标签'] = df['商品标签'].astype(str)

    # 2. 处理缺失值
    df['价格'] = df['价格'].fillna(df['价格'].median())
    df['评价数'] = df['评价数'].fillna(df['评价数'].median())
    df['好评率'] = df['好评率'].fillna(df['好评率'].mean())
    df['想要人数'] = df['想要人数'].fillna(0)
    df['是否包邮'] = df['是否包邮'].fillna(0)

    # 3. 清洗异常值
    df = df[(df['价格'] > 0) & (df['价格'] < 99999)]  # 价格不应太大
    df = df[(df['评价数'] >= 0)]
    df = df[(df['好评率'] >= 0) & (df['好评率'] <= 100)]
    df = df[(df['想要人数'] >= 0)]

    # 清洗后查看数据类型和缺失值
    # print(df.dtypes)
    # print(df.isnull().sum())
    print(f"数据清洗完成，共有{len(df)}条数据。")

    # 保存清洗后的数据到新的CSV文件
    output_file = os.path.join(output_dir, f"{item_name}_cleaned_items.csv")
    df.to_csv(output_file, index=False, encoding='utf-8-sig')  # 使用utf-8-sig编码, 解决CSV文件中的BOM问题
    print(f"清洗后的数据已保存至：{output_file}")