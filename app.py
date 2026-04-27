import streamlit as st
import chromadb
import ollama
import os

from ingest_folder import run_ingestion

# --- 1. 頁面基本設定 ---
st.set_page_config(page_title="🏠 本地 AI 運動聊天室 (Ollama)", page_icon="🏀")
st.title("🏟️ 本地專屬 RAG 搜尋系統")

# --- 2. 初始化資料庫 ---
client_db = chromadb.PersistentClient(path="./chroma_db")
collection = client_db.get_collection(name="sports_news")

# --- 3. 側邊欄 ---
with st.sidebar:
    st.header("📤 上傳新文件")
    uploaded_file = st.file_uploader("選擇檔案 (PDF, DOCX, MD, TXT)", type=["pdf", "docx", "md", "txt"])
    
    if uploaded_file is not None:
        # 儲存上傳的檔案到 my_data 目錄
        save_path = os.path.join("./my_data", uploaded_file.name)
        with open(save_path, "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.success(f"檔案 {uploaded_file.name} 已暫存！")
        
        # 執行入庫按鈕
        if st.button("🚀 開始同步到資料庫"):
            with st.spinner("正在切片並存入資料庫..."):
                msg = run_ingestion()
                st.balloons()
                st.success(msg)
                st.rerun()

    st.divider()
    st.header("📚 知識庫內容")
    if os.path.exists("./my_data"):
        data_files = os.listdir("./my_data")
        # 支援顯示與下載
        for file in data_files:
            file_path = os.path.join("./my_data", file)
            ext = os.path.splitext(file)[1].lower()
            icon = "📄"
            if ext == ".pdf": icon = "📕"
            elif ext == ".md": icon = "📝"
            elif ext == ".docx": icon = "📘"
            
            col1, col2 = st.sidebar.columns([4, 1])
            col1.write(f"{icon} {file}")
            
            # 讀取檔案提供下載
            with open(file_path, "rb") as f:
                col2.download_button(
                    label="💾",
                    data=f,
                    file_name=file,
                    mime="application/octet-stream",
                    key=f"dl_{file}"
                )
    
    if st.button("🔄 刷新知識庫清單"):
        st.rerun()
    
    st.divider()
    st.success("✅ 目前使用本地 Ollama (Llama 3.2)")
    st.info("💡 提示：搜尋廣度已調至最大 (n=5)")

# --- 4. 初始化聊天紀錄 ---
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- 5. 對話處理 ---
if prompt := st.chat_input("請輸入問題..."):
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        # A. 取得目前知識庫的所有檔名，用來判斷使用者是否在問特定檔案
        all_files = []
        if os.path.exists("./my_data"):
            all_files = os.listdir("./my_data")

        # 偵測問題中是否提到特定檔案
        target_file = None
        for f in all_files:
            if f in prompt:
                target_file = f
                break

        # B. 檢索資料庫
        if target_file:
            # 效能優化：針對本地模型，將片段減少到 4 筆，平衡速度與精確度
            results = collection.query(
                query_texts=[prompt], 
                n_results=4, 
                where={"filename": target_file}
            )
            st.info(f"🎯 已鎖定檔案：{target_file} (效能優化模式)")
        else:
            # 一般搜尋只抓 3 筆，追求最快速度
            results = collection.query(query_texts=[prompt], n_results=3)
        
        if results['documents'] and results['documents'][0]:
            combined_context = ""
            for i, doc in enumerate(results['documents'][0]):
                combined_context += f"\n--- 資料片段 {i+1} ---\n{doc}\n"
            
            # --- 極簡 Prompt ---
            ai_prompt = f"""請根據以下資料簡潔回答問題。若資料無關，請回不知道。
            
            資料內容：
            {combined_context}
            
            問題：{prompt}
            """
            
            with st.spinner("思考中..."):
                try:
                    response_stream = ollama.chat(
                        model='llama3.2', 
                        messages=[
                            {'role': 'system', 'content': '你是一個簡潔精確的助手。'},
                            {'role': 'user', 'content': ai_prompt},
                        ],
                        stream=True
                    )

                    import json
                    # 使用 list 來規避 nonlocal 的作用域問題
                    control_state = [True] 

                    def stream_generator():
                        for chunk in response_stream:
                            # 檢查是否為第一塊資料
                            if control_state[0]:
                                print("\n--- Ollama 原始 JSON 結構範例 ---")
                                # 將 ChatResponse 物件轉換為字典
                                chunk_dict = chunk.model_dump() if hasattr(chunk, 'model_dump') else dict(chunk)
                                print(json.dumps(chunk_dict, indent=4, ensure_ascii=False))
                                print("--------------------------------\n")
                                control_state[0] = False

                            yield chunk['message']['content']
                    # 讓文字一個字一個字跳出來
                    full_response = st.write_stream(stream_generator())
                    
                    st.caption(f"💡 檢索來源：{', '.join(results['ids'][0])}")
                except Exception as e:
                    full_response = f"❌ 本地連線失敗：{str(e)}"
                    st.error(full_response)
        else:
            full_response = "資料庫查無資訊。"
            message_placeholder.markdown(full_response)

        st.session_state.messages.append({"role": "assistant", "content": full_response})
