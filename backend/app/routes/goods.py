import csv
import os

from fastapi import APIRouter, HTTPException
from typing import List, Dict
from pydantic import BaseModel

router = APIRouter()

class CrawlRequest(BaseModel):
    keyword: str
    pages: int

# 提取 CSV 文件的需要字段
def extract_fields_from_csv(csv_file: str) -> List[Dict[str, str]]:
    try:
        print(f"开始读取CSV文件: {csv_file}")
        extracted_data = []

        with open(csv_file, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)  # DictReader自动使用第一行作为字段名

            for idx, row in enumerate(reader, start=1):
                # 验证所需字段是否存在
                required_fields = ['商品名称', '价格', '商品链接', '卖家地址', '卖家ID',
                                 '商品标签', '想要人数', '图片链接', '是否包邮', '评价数', '好评率']
                if all(field in row for field in required_fields):
                    extracted_data.append({
                        "序号": str(idx),  # 转换为字符串
                        "商品名称": str(row['商品名称']),
                        "价格": str(row['价格']),
                        "商品链接": str(row['商品链接']),
                        "卖家地址": str(row['卖家地址']),
                        "卖家ID": str(row['卖家ID']),
                        "商品标签": str(row['商品标签']),
                        "想要人数": str(row['想要人数']),
                        "图片链接": str(row['图片链接']),
                        "是否包邮": str(row['是否包邮']),
                        "评价数": str(row['评价数']),
                        "好评率": str(row['好评率'])
                    })
                else:
                    print(f"警告: 第{idx}行缺少必要字段")

        print(f"成功读取{len(extracted_data)}条数据")
        return extracted_data

    except Exception as e:
        print(f"处理CSV文件时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"CSV处理失败: {str(e)}")


@router.post("/cp", response_model=List[Dict[str, str]])
async def crawl_and_process(req: CrawlRequest):
    from backend.app.core.workflow import workflow

    keyword = req.keyword
    pages = req.pages

    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"目录 {data_dir} 创建成功!")

    file_path = os.path.join(data_dir, f"{keyword}_items.csv")
    workflow(keyword, pages, file_path)  # workflow 函数生成文件，并保存到指定路径
    # 提取 CSV 文件中的数据
    try:
        results = extract_fields_from_csv(file_path)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the CSV file: {str(e)}")

@router.get("/cp")
async def crawl_and_process_get():
    return {"message": "Use POST method to crawl and process data."}