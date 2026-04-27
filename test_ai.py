import google.generativeai as genai

# 1. 設定 API Key
API_KEY = "" # 請填入您的 API Key
genai.configure(api_key=API_KEY)

print("正在查詢你可用的模型清單...")

try:
    # 列出所有可用的
    available_models = []
    for m in genai.list_models():
        if 'generateContent' in m.supported_generation_methods:
            available_models.append(m.name)
            print(f"找到可用模型: {m.name}")

    if not available_models:
        print("沒有找到任何可用模型，請檢查 API Key 是否有效。")
    else:
        # 自動挑選清單中的第一個模型來測試
        target_model = available_models[0]
        print(f"\n嘗試使用第一個模型: {target_model}")
        
        model = genai.GenerativeModel(target_model)
        response = model.generate_content("你好，這是一個連線測試。")
        print("\nAI 回應：")
        print(response.text)

except Exception as e:
    print(f"\n連線失敗！錯誤訊息：\n{str(e)}")
