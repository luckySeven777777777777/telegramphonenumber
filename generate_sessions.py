from telethon import TelegramClient
import pandas as pd
import os

API_ID = 30866851
API_HASH = "af93debbb0729a56f347714b56153263"

def normalize_phone(phone):
    return "".join(filter(str.isdigit, str(phone)))

df = pd.read_excel("accounts.xlsx")
os.makedirs("sessions", exist_ok=True)

for _, row in df.iterrows():
    phone = normalize_phone(row["phone"])
    session_path = f"sessions/{phone}"

    print(f"\n=== 正在登录 {phone} ===")

    with TelegramClient(session_path, API_ID, API_HASH) as client:
        client.start(phone="+" + phone)  # ⚠️ 只在代码里补 +
        print(f"✅ {phone} 登录成功")

print("\n🎉 session 全部生成完成")
