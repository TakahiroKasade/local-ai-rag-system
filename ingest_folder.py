import chromadb
import os
import fitz  # PyMuPDF
import docx

def run_ingestion():
    # 1. 初始化資料庫
    client = chromadb.PersistentClient(path="./chroma_db")
    try:
        client.delete_collection(name="sports_news")
    except:
        pass
    collection = client.get_or_create_collection(name="sports_news")

    # 2. 設定參數
    DATA_FOLDER = "./my_data"
    CHUNK_SIZE = 600   # 稍微增加塊的大小，確保上下文完整
    CHUNK_OVERLAP = 100 # 增加重疊，避免關鍵字被切斷

    def split_text(text, size, overlap):
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i:i + size])
        return chunks

    print(f"🚀 PyMuPDF 優化版入庫程式啟動...")

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return "資料夾已建立，請放入檔案。"

    file_count = 0
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        full_content = ""
        
        # --- 處理 PDF 檔 (改用 PyMuPDF) ---
        if filename.endswith(".pdf"):
            print(f"📕 正在精準解析 PDF: {filename}")
            try:
                doc = fitz.open(file_path)
                for page in doc:
                    full_content += page.get_text("text") + "\n"
                doc.close()
            except Exception as e:
                print(f"❌ PDF 解析失敗: {e}")
                continue
        elif filename.endswith(".docx"):
            try:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    full_content += para.text + "\n"
            except: continue

        if full_content.strip():
            chunks = split_text(full_content, CHUNK_SIZE, CHUNK_OVERLAP)
            documents, ids, metadatas = [], [], []
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{filename}_{i}")
                metadatas.append({"filename": filename, "chunk_index": i})
            collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
            file_count += 1
    
    return f"🎉 同步完成！共處理 {file_count} 個檔案。"

if __name__ == "__main__":
    print(run_ingestion())
