import json
import mysql.connector
import re
import os

# 確定 JSON 檔案的絕對路徑
json_file_path = os.path.join('C:\\Users\\timmy\\Desktop\\Welp\\Wehelp Phase 2\\2024.05.27\\taipei-day-trip\\data', 'taipei-attractions.json')

# 建立 MySQL 連接
conn = mysql.connector.connect(
    user="root",
    password="Qoo9898t@",
    host="localhost",
    database="taipei_attractions"
)

# 建立 Cursor 物件，用來對資料庫執行 SQL 指令
cursor = conn.cursor()

# 讀取 JSON 檔案
with open(json_file_path, 'r', encoding='utf-8') as file:
    data = json.load(file)

# 使用正則表達式過濾非 JPG 和 PNG 的網址
url_pattern = re.compile(r'https?://[^ ]*\.(?:jpg|jpeg|png)', re.IGNORECASE)

# 遍歷景點並插入到資料庫中
for attraction in data['result']['results']:
    name = attraction['name']
    category = attraction.get('CAT', '')
    mrt = attraction.get('MRT', '')
    description = attraction.get('description', '')
    address = attraction.get('address', '')
    transport = attraction.get('direction', '')
    longitude = attraction.get('longitude', '')
    latitude = attraction.get('latitude', '')
    images_list = url_pattern.findall(attraction.get('file', ''))
    images = ', '.join(images_list)  # 使用逗號和空格分隔圖片網址

    # 檢查 images 是否為空
    if images:
        print(f"Inserting: {images}")  # 調試信息，檢查 images 字串
        sql = """INSERT INTO attractions (name, category, mrt, description, address, transport, longitude, latitude, images)
                 VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)"""
        values = (name, category, mrt, description, address, transport, longitude, latitude, images)
        cursor.execute(sql, values)

# 提交事務
conn.commit()

# 關閉連接
cursor.close()
conn.close()