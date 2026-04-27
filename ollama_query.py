import chromadb
import ollama

# 1. 連接 ChromaDB 資料庫
# 這裡指向您專案中的 chroma_db 資料夾
client = chromadb.PersistentClient(path="./chroma_db")

try:
    collection = client.get_collection(name="sports_news")
    print("✅ 成功連接到 ChromaDB (sports_news)")
except Exception as e:
    print(f"❌ 找不到資料庫：{e}")
    exit()

print("==============================================")
print("  🏟️  Ollama 本地端 RAG 搜尋系統 (Llama 3.2)  ")
print("==============================================")
print("系統：我現在完全在您的電腦本地執行，不需 API Key！")
print("(輸入 'exit' 結束程式)")

while True:
    user_query = input("\n你問：")
    
    if user_query.lower() in ['exit', 'quit', '離開']:
        print("系統：掰掰！下次見。")
        break

    # 2. 檢索最相關的資料
    results = collection.query(
        query_texts=[user_query],
        n_results=1
    )

    if results['documents'] and results['documents'][0]:
        retrieved_context = results['documents'][0][0]
        
        # 3. 使用 Ollama 本地模型生成回答
        print("Ollama 正在思考中...", end="\r")
        
        response = ollama.chat(
            model='llama3.2',
            messages=[
                {
                    'role': 'system',
                    'content': f'你是一個專業的體育播報員。請根據以下參考資料回答問題。如果資料中沒提到，請回答你不知道。\n\n參考資料：\n{retrieved_context}'
                },
                {
                    'role': 'user',
                    'content': user_query
                },
            ]
        )
        
        print(f"AI 回答：{response['message']['content']}")
    else:
        print("AI：抱歉，資料庫裡沒有相關資訊。")
