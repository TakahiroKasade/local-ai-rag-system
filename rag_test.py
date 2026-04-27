from google import genai
import os

# 1. 設定 API Key
API_KEY = "" # 請填入您的 API Key
client = genai.Client(api_key=API_KEY)

# 2. 讀取資料檔案 (修正路徑為 my_data/sports_data.txt)
data_path = "my_data/sports_data.txt"

if not os.path.exists(data_path):
    print(f"錯誤：找不到資料檔案 {data_path}")
    exit()

with open(data_path, "r", encoding="utf-8") as f:
    sports_knowledge = f.read()

print("==============================================")
print("  🏀 運動資料互動聊天室 (輸入 'exit' 結束)  ")
print("==============================================")
print(f"系統：我已經讀完您的 {data_path} 了，您可以問我任何關於裡面的問題！")

while True:
    user_input = input("\n你：")
    
    if user_input.lower() in ['exit', 'quit', '離開']:
        print("AI：掰掰！祝你今天也是個全壘打的一天！")
        break

    # RAG 的 Prompt 核心
    prompt = f"""
    你是專屬的運動資料助手。請根據下方參考資料回答問題。
    如果問題在資料中找不到答案，請回答：「抱歉，我的參考資料裡沒提到這個。」

    --- 參考資料 ---
    {sports_knowledge}
    ----------------

    使用者提問：{user_input}
    """

    print("AI 思考中...", end="\r")
    try:
        response = client.models.generate_content(
            model='gemini-1.5-flash',
            contents=prompt
        )
        print(f"AI：{response.text}")
    except Exception as e:
        print(f"AI：發生錯誤了... {str(e)}")
