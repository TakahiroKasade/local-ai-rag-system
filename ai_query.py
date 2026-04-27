import chromadb
import google.generativeai as genai

# 1. 設定 Gemini API Key
API_KEY = "" # 請填入您的 API Key
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-2.5-flash')

# 2. 連接 ChromaDB 資料庫
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="sports_news")

print("==============================================")
print("  🏟️  專業運動 RAG 搜尋系統 (資料庫版)  ")
print("==============================================")
print("系統：已連接 ChromaDB。請輸入問題，我會從資料庫檢索答案。")
print("(輸入 'exit' 可結束程式)")

while True:
    user_query = input("\n你問：")
    
    if user_query.lower() == 'exit':
        print("系統：再見！祝你有個愉快的一天。")
        break

    # 3. 核心步驟：從資料庫檢索最相關的資料
    # n_results=1 代表只找最相關的一筆
    results = collection.query(
        query_texts=[user_query],
        n_results=1
    )

    # 取得檢索到的內容
    if results['documents'] and results['documents'][0]:
        retrieved_context = results['documents'][0][0]
        source_id = results['ids'][0][0]
        
        # 4. 將檢索到的資料交給 AI 進行生成
        prompt = f"""
        你是一個專業的體育播報員。請根據以下「從資料庫檢索到的資料」來回答使用者的問題。
        如果資料中找不到答案，請老實說你不知道。

        --- 檢索到的資料 ---
        {retrieved_context}
        -------------------

        使用者提問：{user_query}
        """

        print("AI 檢索並思考中...", end="\r")
        response = model.generate_content(prompt)
        
        print(f"AI 回答：{response.text}")
        print(f" (資料來源 ID: {source_id})")
    else:
        print("AI：抱歉，我在資料庫裡找不到任何相關資訊。")
