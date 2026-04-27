import chromadb
import google.generativeai as genai

# 1. 設定 API Key (之後計算向量會用到)
API_KEY = "" # 請填入您的 API Key
genai.configure(api_key=API_KEY)

print("正在初始化 ChromaDB 向量資料庫...")

# 2. 初始化 ChromaDB (資料會儲存在 ./chroma_db 資料夾)
client = chromadb.PersistentClient(path="./chroma_db")

# 3. 建立或取得收藏庫 (就像是 SQL 的資料表)
# 我們命名為 "sports_news"
collection = client.get_or_create_collection(name="sports_news")

# 4. 讀取你的運動資料檔案
try:
    with open("sports_data.txt", "r", encoding="utf-8") as f:
        document_content = f.read()
    
    print("正在將 sports_data.txt 的內容存入資料庫...")

    # 5. 存入資料庫
    # documents: 原始文字內容
    # ids: 這筆資料的唯一標記
    # metadatas: 額外的標籤資訊 (方便之後過濾)
    collection.add(
        documents=[document_content],
        ids=["news_001"],
        metadatas=[{"source": "local_file", "type": "sports_news"}]
    )

    print("\n✅ 成功！資料已永久存入向量資料庫。")
    print("你現在應該可以在 VS Code 左側看到一個 'chroma_db' 資料夾了。")

except FileNotFoundError:
    print("❌ 錯誤：找不到 sports_data.txt。請確保檔案存在專案目錄中。")
except Exception as e:
    print(f"❌ 發生未知錯誤：{str(e)}")
