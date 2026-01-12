from telethon import TelegramClient
import os

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

phone = os.getenv("LOGIN_PHONE")  # 例如 17408999258（不加+）

if not phone:
    raise RuntimeError("请设置环境变量 LOGIN_PHONE")

os.makedirs("sessions", exist_ok=True)

client = TelegramClient(f"sessions/{phone}", API_ID, API_HASH)
client.start(phone=phone)

print("✅ 登录成功，session 已生成")
client.disconnect()