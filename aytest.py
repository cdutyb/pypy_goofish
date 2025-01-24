import pandas as pd

good = "rtx 4090"
# 读取CSV文件
df = pd.read_csv(f'cleaned_data/{good}_cleaned_items.csv')

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
filtered_df = df[df['价格差绝对值'] > 2 * std_price].copy()
unfiltered_df = df[df['价格差绝对值'] <= 2 * std_price].copy()

# 使用.loc明确指定赋值位置
filtered_df.loc[:, '均值er'] = filtered_df['价格'].mean()
unfiltered_df.loc[:, '均值er'] = unfiltered_df['价格'].mean()

filtered_df.loc[:, '中位数er'] = filtered_df['价格'].median()
unfiltered_df.loc[:, '中位数er'] = unfiltered_df['价格'].median()

# 删除辅助列
# filtered_df = filtered_df.drop(columns=['价格差绝对值'])
# unfiltered_df = unfiltered_df.drop(columns=['价格差绝对值'])

# 将筛选后的数据保存到不同的CSV文件
filtered_df.to_csv(f'{good}_filtered_prices.csv', index=False, encoding='utf-8-sig')
unfiltered_df.to_csv(f'{good}_unfiltered_prices.csv', index=False, encoding='utf-8-sig')
