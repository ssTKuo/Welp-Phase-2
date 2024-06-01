# HTTPException，來自 fastapi 模組，用於在 API 路由中引發 HTTP 錯誤。當發生錯誤時，您可以使用 HTTPException 返回特定的 HTTP 狀態碼和錯誤信息。
# Query，來自 fastapi 模組，用於處理查詢參數。它允許您設置查詢參數的默認值、數據類型和驗證條件。例如，page: int = Query(0, ge=0) 設置 page 參數的默認值為 0，且該參數必須大於或等於 0。
# List 和 Optional，來自 typing 模組，用於類型註釋。List 表示列表類型，Optional 表示參數是可選的，可以是某種類型或 None。
# logging 是 Python 標準庫中的一個模組，用於記錄應用程式運行過程中的日誌信息。日誌可以幫助開發人員了解應用程式的運行狀況，發現和排查錯誤。
# Path 用於定義路徑參數的驗證。
from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import FileResponse
from typing import Optional
import mysql.connector



app=FastAPI()
# 資料庫連接配置
db_config = {
    'user': 'root',
    'password': 'Qoo9898t@',
    'host': 'localhost',
    'database': 'taipei_attractions'
}


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")

#新增的Attraction API (取得景點資料表)
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
            count_query = ("""
                SELECT COUNT(*) as total FROM attractions 
                WHERE name LIKE %s OR category LIKE %s 
                OR description LIKE %s OR address LIKE %s 
                OR transport LIKE %s OR mrt LIKE %s
            """)
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
            query = ("""
                SELECT * FROM attractions 
                WHERE name LIKE %s OR mrt LIKE %s
                LIMIT %s OFFSET %s
            """)
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

    except mysql.connector.Error:
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        cursor.close()
        conn.close()
        
#新增的Attraction API (根據景點編號取得景點資料)
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

    except mysql.connector.Error as err:
        print(f"Database Error: {err}")
        raise HTTPException(status_code=500, detail="伺服器內部錯誤。")

    finally:
        cursor.close()
        conn.close()

#新增的MRT Station API (取得捷運站名稱列表)
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

    except mysql.connector.Error as err:
        raise HTTPException(status_code=500, detail="Database connection error")
    finally:
        cursor.close()
        conn.close()       