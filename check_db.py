import chromadb

# 連接資料庫
client = chromadb.PersistentClient(path="./chroma_db")
collection = client.get_collection(name="sports_news")

# 抓出目前資料庫裡所有的資料
results = collection.get()

print("==============================================")
print("  🔍 向量資料庫現狀檢查")
print("==============================================")

if not results['ids']:
    print("資料庫目前是空的！")
else:
    print(f"總共找到 {len(results['ids'])} 筆資料：\n")
    for i, doc_id in enumerate(results['ids']):
        # 從 metadata 拿檔名，如果沒標註就顯示未知
        metadata = results['metadatas'][i] if results['metadatas'] else {}
        filename = metadata.get('filename', '未知檔案')
        
        # 顯示前 50 個字作為內容預覽
        content_preview = results['documents'][i][:50].replace('\n', ' ')
        
        print(f"[{i+1}] 檔案: {filename}")
        print(f"    ID: {doc_id}")
        print(f"    內容預覽: {content_preview}...")
        print("-" * 30)

print("\n提示：如果沒看到你的 PDF，請執行 python ingest_folder.py")
