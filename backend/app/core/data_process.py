import pandas as pd
import os

# 定义数据清洗函数
def clean_data(file_path):
    try:
        # 加载数据
        df = pd.read_csv(file_path)

        # 检查并转换数据类型
        try:
            if df['好评率'].dtype == 'object':
                df['好评率'] = df['好评率'].str.replace('%', '')
                df['好评率'] = pd.to_numeric(df['好评率'], errors='coerce')
            df['价格'] = pd.to_numeric(df['价格'], errors='coerce')
            df['评价数'] = pd.to_numeric(df['评价数'], errors='coerce')
            df['好评率'] = pd.to_numeric(df['好评率'], errors='coerce')
            df['想要人数'] = pd.to_numeric(df['想要人数'], errors='coerce')

            df['是否包邮'] = df['是否包邮'].astype(int)
            df['商品名称'] = df['商品名称'].astype(str)
            df['商品链接'] = df['商品链接'].astype(str)
            df['卖家地址'] = df['卖家地址'].astype(str)
            df['卖家ID'] = df['卖家ID'].astype(str)
            df['商品标签'] = df['商品标签'].astype(str)
        except Exception as e:
            print(f"数据类型转换时出错: {str(e)}")
            raise

        # 处理缺失值
        try:
            df['价格'] = df['价格'].fillna(df['价格'].median())
            df['评价数'] = df['评价数'].fillna(df['评价数'].median())
            df['好评率'] = df['好评率'].fillna(df['好评率'].mean())
            df['想要人数'] = df['想要人数'].fillna(0)
            df['是否包邮'] = df['是否包邮'].fillna(0)
        except Exception as e:
            print(f"处理缺失值时出错: {str(e)}")
            raise

        # 清洗异常值
        try:
            df = df[(df['价格'] > 0) & (df['价格'] < 99999)]
            df = df[(df['评价数'] >= 0)]
            df = df[(df['好评率'] >= 0) & (df['好评率'] <= 100)]
            df = df[(df['想要人数'] >= 0)]
        except Exception as e:
            print(f"清洗异常值时出错: {str(e)}")
            raise

        # 保存清洗后的数据到原文件
        try:
            df.to_csv(file_path, index=False, encoding='utf-8-sig')
            print('数据清洗完成')
        except Exception as e:
            print(f"保存清洗后的数据时出错: {str(e)}")
            raise

    except Exception as e:
        print(f"数据清洗过程中发生严重错误: {str(e)}")
        raise

def sort_data(file_path):
    try:
        df = pd.read_csv(file_path)

        try:
            # 计算价格的均值和标准差
            mean_price = df['价格'].mean()
            std_price = df['价格'].std()

            # 计算价格差的绝对值
            df['价格差绝对值'] = abs(df['价格'] - mean_price)

            # 均值
            df['均值'] = mean_price

            # 中位数
            df['中位数'] = df['价格'].median()

            # 根据条件筛选数据
            df = df[df['价格差绝对值'] <= 2 * std_price]
        except Exception as e:
            print(f"计算统计量时出错: {str(e)}")
            raise

        # 设置权重
        try:
            weight_price = 0.15
            weight_review_count = 0.25
            weight_positive_rate = 0.55
            weight_want_count = 0.05

            # 标准化处理
            df['价格标准化'] = 1 - ((df['价格'] - df['价格'].min()) / (df['价格'].max() - df['价格'].min()))
            df['评价数标准化'] = (df['评价数'] - df['评价数'].min()) / (df['评价数'].max() - df['评价数'].min())
            df['好评率标准化'] = (df['好评率'] - df['好评率'].min()) / (df['好评率'].max() - df['好评率'].min())
            df['想要人数标准化'] = (df['想要人数'] - df['想要人数'].min()) / (df['想要人数'].max() - df['想要人数'].min())

            # 计算综合评分
            df['综合评分'] = round((df['价格标准化'] * weight_price +
                              df['评价数标准化'] * weight_review_count +
                              df['好评率标准化'] * weight_positive_rate +
                              df['想要人数标准化'] * weight_want_count), 4) * 100
        except Exception as e:
            print(f"计算综合评分时出错: {str(e)}")
            raise

        # 排序并保存
        try:
            df_sorted = df.sort_values(by='综合评分', ascending=False)
            df_sorted.to_csv(file_path, index=False, encoding='utf-8-sig')
            print('数据排序完成')
        except Exception as e:
            print(f"保存排序后的数据时出错: {str(e)}")
            raise

    except Exception as e:
        print(f"数据排序过程中发生严重错误: {str(e)}")
        raise