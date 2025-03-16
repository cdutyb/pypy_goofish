import csv
import os
from fastapi import APIRouter, HTTPException
from typing import List, Dict, Any
from pydantic import BaseModel


router = APIRouter()
extracted_data = []
filtered_data = []  # Store filtered data

# 请求模型
class CrawlRequest(BaseModel):
    keyword: str
    pages: int

# 提取 CSV 文件的需要字段，并支持分页
async def extract_fields_from_csv(csv_file: str) -> Dict[str, Any]:
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

        # 将原始数据传递给语义过滤函数
        await apply_semantic_filter()

        # 计算总页数 (使用过滤后的数据)
        total_pages = (len(filtered_data) // 30) + (1 if len(filtered_data) % 30 > 0 else 0)

        return {
            "products": filtered_data[:30],  # 默认返回第一页的过滤后商品数据
            "totalPages": total_pages  # 总页数
        }

    except Exception as e:
        print(f"处理CSV文件时出错: {str(e)}")
        import traceback
        print(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"CSV处理失败: {str(e)}")

# 应用语义过滤
async def apply_semantic_filter():
    try:
        # 延迟导入避免循环引用
        from backend.app.core.zhipuai.Semantic_Filtering import SemanticFilter
        global extracted_data, filtered_data

        semantic_filter = SemanticFilter()
        valid_products, invalid_count = await semantic_filter.filter_invalid_products(extracted_data)
        filtered_data = valid_products
        print(f"语义过滤: 过滤了 {invalid_count} 件商品, 剩余 {len(filtered_data)} 件")
    except Exception as e:
        print(f"语义过滤错误: {str(e)}")
        # 如果过滤失败，使用原始数据
        filtered_data = extracted_data

# 获取过滤后的商品数据
async def get_filtered_goods_data():
    global filtered_data
    return filtered_data

# 后端API路由
@router.post("/cp", response_model=Dict[str, Any])
async def crawl_and_process(req: CrawlRequest):
    try:
        from backend.app.core.workflow import workflow

        keyword = req.keyword
        pages = req.pages

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        data_dir = os.path.join(base_dir, "data")
        try:
            if not os.path.exists(data_dir):
                os.makedirs(data_dir, exist_ok=True)
                print(f"目录 {data_dir} 创建成功!")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"创建数据目录失败: {str(e)}")

        file_path = os.path.join(data_dir, f"{keyword}_items.csv")
        try:
            workflow(keyword, pages, file_path)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"数据爬取失败: {str(e)}")

        try:
            results = await extract_fields_from_csv(file_path)
            return results
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"读取CSV文件失败: {str(e)}")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"处理请求时发生未知错误: {str(e)}")

@router.get("/page")
async def get_page_data(page: int = 1):
    try:
        # 每页30条数据
        page_size = 30
        global filtered_data
        total_items = len(filtered_data)

        # 检查页码是否有效
        if page < 1 or (total_items > 0 and page > (total_items // page_size + (1 if total_items % page_size > 0 else 0))):
            raise HTTPException(status_code=400, detail="无效的页码")

        # 获取对应页的数据
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        page_data = filtered_data[start_index:end_index]

        return {
            "page": page,
            "totalPages": (total_items // page_size) + (1 if total_items % page_size > 0 else 0),
            "data": page_data
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取分页数据失败: {str(e)}")

@router.get("/cp")
async def crawl_and_process_get():
    return {"message": "Use POST method to crawl and process data."}