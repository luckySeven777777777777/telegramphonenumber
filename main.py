from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import pandas as pd
import os
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

TMP_SESSION_DIR = "./sessions"
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

    # --- 之前的检查逻辑保持不变 ---
    contacts = [
        InputPhoneContact(client_id=0, phone=normalize_phone(row["phone"]), first_name="Check", last_name="")
        for _, row in contacts_df.iterrows()
    ]

    if contacts:
        result = await client(ImportContactsRequest(contacts))
        results_list = []
        registered_users = {u.phone: u for u in result.users}

        for contact in contacts:
            p = contact.phone
            user = registered_users.get(p) or registered_users.get(f"1{p}")

            if user:
                if user.username:
                    results_list.append([p, "✅ 已开通", "Username", f"@{user.username}"])
                else:
                    results_list.append([p, "✅ 已开通", "Tg Data", f"ID: {user.id}"])
            else:
                results_list.append([p, "❌ 未开通", "No Tg Data", "-"])

        # 保存 Excel
        output_file = f"checked_{phone}.xlsx"
        df_final = pd.DataFrame(results_list, columns=["原始号码 (+1)", "状态", "分类结果", "详细信息 (Username/ID)"])
        df_final.to_excel(output_file, index=False)
        print(f"[FINISH] {phone} 检查完成，结果已存入 {output_file}")

        # ================== 核心新增代码：发回手机 ==================
        try:
            # "me" 代表发给账号自己（即你的 Telegram 收藏夹/Saved Messages）
            # 这样你打开手机 Telegram 就能看到这个文件
            await client.send_file("me", output_file, caption=f"📊 检查完成！\n账号: +{phone}\n时间: May 6, 2026")
            print(f"[SENT] 结果文件已发送至 Telegram 收藏夹")
        except Exception as e:
            print(f"[SEND ERROR] 发送文件失败: {e}")
        # =========================================================

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
