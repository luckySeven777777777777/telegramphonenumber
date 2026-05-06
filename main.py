from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import pandas as pd
import os
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

TMP_SESSION_DIR = "/tmp/telegram_sessions"
os.makedirs(TMP_SESSION_DIR, exist_ok=True)


def normalize_phone(phone):
    return "".join(filter(str.isdigit, str(phone)))


accounts_df = pd.read_excel("accounts.xlsx")


async def run_account(phone, contacts_df):
    session_path = os.path.join(TMP_SESSION_DIR, phone)
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"[ERROR] {phone} 未登录")
        await client.disconnect()
        return

    # 准备导入列表
    contacts = [
        InputPhoneContact(client_id=0, phone=normalize_phone(row["phone"]), first_name="Check", last_name="")
        for _, row in contacts_df.iterrows()
    ]

    if contacts:
        # 执行检查任务
        result = await client(ImportContactsRequest(contacts))
        
        # 结果分类存储容器
        results_list = []
        # 将返回的已注册用户存入字典，方便匹配
        registered_users = {u.phone: u for u in result.users}

        for contact in contacts:
            p = contact.phone
            user = registered_users.get(p) or registered_users.get(f"1{p}") # 兼容加不加1的情况

            if user:
                if user.username:
                    # 分类：Username
                    results_list.append([p, "✅ 已开通", "Username", f"@{user.username}"])
                else:
                    # 分类：Tg Data
                    results_list.append([p, "✅ 已开通", "Tg Data", f"ID: {user.id}"])
            else:
                # 分类：No Tg Data
                results_list.append([p, "❌ 未开通", "No Tg Data", "-"])

        # 将结果保存为 Excel，对应你截图的效果
        df_final = pd.DataFrame(results_list, columns=["原始号码 (+1)", "状态", "分类结果", "详细信息 (Username/ID)"])
        df_final.to_excel(f"checked_{phone}.xlsx", index=False)
        print(f"[FINISH] {phone} 检查完成，结果已存入 checked_{phone}.xlsx")

    await client.disconnect()



async def main():
    for _, account in accounts_df.iterrows():
        phone = normalize_phone(account["phone"])
        contacts_file = f"contacts/{phone}.xlsx"

        if not os.path.exists(contacts_file):
            print(f"[SKIP] {phone} 没有联系人文件")
            continue

        contacts_df = pd.read_excel(contacts_file)
        await run_account(phone, contacts_df)

        # 防止 Telegram 风控
        await asyncio.sleep(60)


asyncio.run(main())
