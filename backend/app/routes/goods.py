import csv
import os
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel

router = APIRouter()
extracted_data = []


# 请求模型
class CrawlRequest(BaseModel):
    keyword: str
    pages: int


# 提取 CSV 文件的需要字段，并支持分页
def extract_fields_from_csv(csv_file: str) -> Dict[str, Any]:
    try:
        print(f"开始读取CSV文件: {csv_file}")
        global extracted_data
        # 清空全局变量，确保每次请求都从新读取CSV文件
        extracted_data = []

        with open(csv_file, mode="r", encoding="utf-8-sig") as file:
            reader = csv.DictReader(file)

            for idx, row in enumerate(reader, start=1):
                required_fields = ['商品名称', '价格', '商品链接', '卖家地址', '卖家ID',
                                   '商品标签', '想要人数', '图片链接', '是否包邮', '评价数', '好评率', '综合评分']
                if all(field in row for field in required_fields):
                    extracted_data.append({
                        "序号": str(idx),
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
                        "好评率": str(row['好评率']),
                        "综合评分": str(row['综合评分'])
                    })

        print(f"成功读取{len(extracted_data)}条数据")

        # 计算总页数
        total_pages = (len(extracted_data) // 30) + (1 if len(extracted_data) % 30 > 0 else 0)

        return {
            "products": extracted_data[:30],  # 默认返回第一页的商品数据
            "totalPages": total_pages  # 总页数
        }

    except Exception as e:
        print(f"处理CSV文件时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"CSV处理失败: {str(e)}")


# 后端API路由
@router.post("/cp", response_model=Dict[str, Any])
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

    # 提取 CSV 文件中的数据并返回分页结果
    try:
        results = extract_fields_from_csv(file_path)
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading the CSV file: {str(e)}")


@router.get("/cp")
async def crawl_and_process_get():
    return {"message": "Use POST method to crawl and process data."}


# 翻页API：通过页码获取分页数据
@router.get("/page")
async def get_page_data(page: int = 1):
    # 每页30条数据
    page_size = 30
    total_items = len(extracted_data)

    # 检查页码是否有效
    if page < 1 or page > (total_items // page_size + (1 if total_items % page_size > 0 else 0)):
        raise HTTPException(status_code=400, detail="Invalid page number")

    # 获取对应页的数据
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    page_data = extracted_data[start_index:end_index]

    return {
        "page": page,
        "totalPages": (total_items // page_size) + (1 if total_items % page_size > 0 else 0),
        "data": page_data
    }
