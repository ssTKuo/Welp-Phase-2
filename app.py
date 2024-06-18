from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional
import mysql.connector

app = FastAPI()

# 配置静态文件目录
app.mount("/static", StaticFiles(directory="static"), name="static")
app.mount("/data", StaticFiles(directory="data"), name="data")
app.mount("/styles", StaticFiles(directory="styles"), name="styles")

# 新增 Jinja2 模板配置
templates = Jinja2Templates(directory="templates")

# 資料庫連接配置
db_config = {
    'user': 'root',
    'password': 'Qoo9898t@',
    'host': 'localhost',
    'database': 'taipei_attractions'
}

# 靜態頁面路由
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")

@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")

@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")

# 新增的Attraction API (取得景點資料表)
@app.get("/api/attractions")
def get_attractions(page: int = Query(0, ge=0), keyword: Optional[str] = Query(None)):
    try:
        # 連接資料庫
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 每頁顯示 12 筆資料
        limit = 12
        offset = page * limit

        # 計算符合條件的資料總數
        if keyword:
            count_query = """
                SELECT COUNT(*) as total FROM attractions 
                WHERE name LIKE %s OR category LIKE %s 
                OR description LIKE %s OR address LIKE %s 
                OR transport LIKE %s OR mrt LIKE %s
            """
            cursor.execute(count_query, (
                f"%{keyword}%", f"%{keyword}%", 
                f"%{keyword}%", f"%{keyword}%", 
                f"%{keyword}%", f"%{keyword}%"
            ))
        else:
            count_query = "SELECT COUNT(*) as total FROM attractions"
            cursor.execute(count_query)

        total_results = cursor.fetchone()['total']

        # 查詢語句
        if keyword:
            query = """
                SELECT * FROM attractions 
                WHERE name LIKE %s OR mrt LIKE %s
                LIMIT %s OFFSET %s
            """
            cursor.execute(query, (
                f"%{keyword}%", f"%{keyword}%", limit, offset))
        else:
            query = "SELECT * FROM attractions LIMIT %s OFFSET %s"
            cursor.execute(query, (limit, offset))

        results = cursor.fetchall()

        # 構建響應資料
        attractions = []
        for row in results:
            images = [img for img in row['images'].split(', ') if img]
            attraction = {
                "id": row['id'],
                "name": row['name'],
                "category": row['category'],
                "description": row['description'],
                "address": row['address'],
                "transport": row['transport'],
                "mrt": row.get('mrt'),             
                "lat": row['latitude'],
                "lng": row['longitude'],
                "images": images
            }
            attractions.append(attraction)

        # 計算下一頁
        next_page = None
        if len(results) == limit:
            next_page = page + 1

        return {"nextPage": next_page, "data": attractions}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    finally:
        cursor.close()
        conn.close()
        
# 新增的Attraction API (根據景點編號取得景點資料)
@app.get("/api/attraction/{attractionId}")
def get_attraction(attractionId: int):
    try:
        # 連接資料庫
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)

        # 查詢景點資料
        cursor.execute("SELECT * FROM attractions WHERE id = %s", (attractionId,))
        attraction = cursor.fetchone()

        # 如果找不到景點，返回 400 錯誤
        if not attraction:
            raise HTTPException(status_code=400, detail="您提供的景點ID不正確或不存在，請再確認。")

        # 分割圖片 URL
        attraction['images'] = attraction['images'].split(', ')

        return {"data": attraction}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"伺服器內部錯誤: {e}")

    finally:
        cursor.close()
        conn.close()

# 新增的MRT Station API (取得捷運站名稱列表)
@app.get("/api/mrts")
def get_mrt_stations():
    try:
        # 連接數據庫
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor(dictionary=True)
        
        # 執行SQL查詢，排除MRT為Null的資料
        query = """
            SELECT mrt, COUNT(*) as count
            FROM attractions
            WHERE mrt IS NOT NULL
            GROUP BY mrt
            ORDER BY count DESC;
        """
        cursor.execute(query)
        results = cursor.fetchall()

        # 构建响应数据
        mrt_stations = [result['mrt'] for result in results]

        return {"data": mrt_stations}

    except mysql.connector.Error as e:
        raise HTTPException(status_code=500, detail=f"Database connection error: {e}")
    finally:
        cursor.close()
        conn.close()