import google.generativeai as genai
import time

# 你的 API Key
API_KEY = "" # 請填入您的 API Key
genai.configure(api_key=API_KEY)

# 測試這三個最核心的模型路徑
# 加上 models/ 前綴可以增加相容性
test_models = [
    'models/gemini-1.5-flash',
    'models/gemini-1.5-pro',
    'models/gemini-2.0-flash'
]

print("==============================================")
print("  🔍 Google API 模型連線診斷工具")
print("==============================================")

for model_name in test_models:
    print(f"正在測試: {model_name}...", end=" ", flush=True)
    try:
        model = genai.GenerativeModel(model_name)
        # 發送一個極短的請求測試連線
        response = model.generate_content("Ping")
        if response.text:
            print("✅ 正常連線！")
    except Exception as e:
        err_msg = str(e)
        if "429" in err_msg:
            print("❌ 限流中 (429: Too Many Requests)")
        elif "404" in err_msg:
            print("❌ 找不到模型 (404: Not Found)")
        else:
            print(f"❌ 錯誤: {err_msg[:60]}...")
    
    # 稍微停頓避免測試太快
    time.sleep(1)

print("\n診斷完成。請選擇標註為 ✅ 的模型填入 app.py 即可！")
