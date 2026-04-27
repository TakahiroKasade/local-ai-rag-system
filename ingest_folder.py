import chromadb
import os
import fitz  # PyMuPDF
import docx
import easyocr
import numpy as np
from PIL import Image
import io

# 初始化 OCR 引擎 (支援繁體中文與英文)
print("⏳ 正在初始化 OCR 引擎 (第一次執行會下載模型，請稍候)...")
reader = easyocr.Reader(['ch_tra', 'en'])

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
    CHUNK_SIZE = 600   
    CHUNK_OVERLAP = 100 

    def split_text(text, size, overlap):
        chunks = []
        for i in range(0, len(text), size - overlap):
            chunks.append(text[i:i + size])
        return chunks

    print(f"🚀 超級 OCR 優化版入庫程式啟動...")

    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
        return "資料夾已建立。"

    file_count = 0
    for filename in os.listdir(DATA_FOLDER):
        file_path = os.path.join(DATA_FOLDER, filename)
        full_content = ""
        
        # --- 處理 PDF 檔 (文字提取 + OCR) ---
        if filename.endswith(".pdf"):
            print(f"📕 正在分析 PDF: {filename}")
            try:
                doc = fitz.open(file_path)
                for page_index, page in enumerate(doc):
                    text = page.get_text("text").strip()
                    
                    # 智慧判定：如果文字太少 (可能是圖片頁)，啟動 OCR
                    if len(text) < 50:
                        print(f"  🔍 第 {page_index+1} 頁文字稀少，啟動 OCR 辨識中...")
                        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 提高解析度以利辨識
                        img_data = pix.tobytes("png")
                        # 執行 OCR
                        result = reader.readtext(img_data, detail=0)
                        text = " ".join(result)
                    
                    full_content += text + "\n"
                doc.close()
            except Exception as e:
                print(f"❌ PDF 處理失敗: {e}")
                continue
                
        # --- 處理 Word 檔 ---
        elif filename.endswith(".docx"):
            try:
                doc = docx.Document(file_path)
                for para in doc.paragraphs:
                    full_content += para.text + "\n"
            except: continue
            
        # --- 處理文字與 MD 檔 ---
        elif filename.endswith(".txt") or filename.endswith(".md"):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    full_content = f.read()
            except: continue

        # --- 開始切片並存入 ---
        if full_content.strip():
            chunks = split_text(full_content, CHUNK_SIZE, CHUNK_OVERLAP)
            documents, ids, metadatas = [], [], []
            for i, chunk in enumerate(chunks):
                documents.append(chunk)
                ids.append(f"{filename}_{i}")
                metadatas.append({"filename": filename, "chunk_index": i})
            collection.upsert(documents=documents, ids=ids, metadatas=metadatas)
            file_count += 1
            print(f"✅ {filename} 處理完成 (含 OCR 掃描)。")
    
    return f"🎉 全格式同步完成！共處理 {file_count} 個檔案。"

if __name__ == "__main__":
    print(run_ingestion())
