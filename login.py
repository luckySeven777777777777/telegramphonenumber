from telethon import TelegramClient
import os

# 这里填你自己的 API 信息
API_ID = 31295509
API_HASH = "2d1e4c49213cc70e07afd487b18d71bc"

phone = "+12282629379"

os.makedirs("sessions", exist_ok=True)

client = TelegramClient(f"sessions/{phone.replace('+', '')}", API_ID, API_HASH)

async def main():
    await client.start(phone=phone)
    print("✅ 登录成功，session 已生成在 sessions 文件夹内")

import asyncio
asyncio.run(main())
