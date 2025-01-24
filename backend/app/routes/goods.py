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
    extracted_data = []
    with open(csv_file, mode="r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        for idx, row in enumerate(reader, start=1):  # 使用 enumerate 添加序号，从 1 开始
            # 从每一行提取需要的字段，并添加序号
            extracted_data.append({
                "序号": idx,
                "商品名称": row["商品名称"],
                "价格": row["价格"],
                "商品链接": row["商品链接"],
                "卖家地址": row["卖家地址"],
                "卖家ID": row["卖家ID"],
                "商品标签": row["商品标签"],
                "想要人数": row["想要人数"],
                "图片链接": row["图片链接"],
                "是否包邮": row["是否包邮"],
                "评价数": row["评价数"],
                "好评率": row["好评率"]
            })
    return extracted_data


@router.post("/crawl_and_process", response_model=List[Dict[str, str]])
async def crawl_and_process(req: CrawlRequest):
    from backend.app.core.workflow import workflow

    keyword = req.keyword
    pages = req.pages

    data_dir = os.path.join("../..", "data")
    if not os.path.exists(data_dir):
        os.makedirs(data_dir, exist_ok=True)
        print(f"目录 {data_dir} 创建成功!")
    else:
        # 如果路径已存在，但不是目录（是文件），则报错
        if not os.path.isdir(data_dir):
            print(f"错误：{data_dir} 已存在且是文件，不能创建目录!")
        else:
            print(f"目录 {data_dir} 已存在!")

    file_path = os.path.join(data_dir, f"{keyword}_items.csv")
    workflow(keyword, pages, file_path)  # workflow 函数生成文件，并保存到指定路径
    # 提取 CSV 文件中的数据
    try:
        results = extract_fields_from_csv(file_path)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the CSV file: {str(e)}")
