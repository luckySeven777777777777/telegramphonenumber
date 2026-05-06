from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
from datetime import datetime
import pandas as pd
import os
import asyncio

# 配置从环境变量读取
API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

TMP_SESSION_DIR = "./sessions"
os.makedirs(TMP_SESSION_DIR, exist_ok=True)

def normalize_phone(phone):
    """只保留数字，处理掉空格、+号等字符"""
    return "".join(filter(str.isdigit, str(phone)))

async def run_account(phone, contacts_df):
    session_path = os.path.join(TMP_SESSION_DIR, phone)
    client = TelegramClient(session_path, API_ID, API_HASH)
    await client.connect()

    if not await client.is_user_authorized():
        print(f"[ERROR] {phone} 未登录")
        await client.disconnect()
        return

    # --- 1. 数据清洗：去掉空行，确保号码是字符串格式 ---
    # 强制将 phone 列转为字符串，并过滤掉空值
    contacts_df['phone'] = contacts_df['phone'].astype(str)
    valid_df = contacts_df[contacts_df['phone'].str.strip() != 'nan'].copy()

    # --- 2. 准备导入列表 ---
    contacts = []
    for _, row in valid_df.iterrows():
        clean_p = normalize_phone(row["phone"])
        if clean_p:
            contacts.append(InputPhoneContact(client_id=0, phone=clean_p, first_name="Check", last_name=""))

    if contacts:
        # 执行检查任务
# 执行检查任务
        result = await client(ImportContactsRequest(contacts))
        
        results_list = []
        # --- 优化点：Key 统一只保留最后 10 位数字（美国号码主体），彻底解决 1 或 +1 的前缀干扰 ---
        registered_users = {normalize_phone(u.phone)[-10:]: u for u in result.users}

        for contact in contacts:
            # 同样取最后 10 位进行匹配
            p_full = contact.phone
            p_suffix = p_full[-10:]
            
            user = registered_users.get(p_suffix)

            if user:
                if user.username:
                    results_list.append([p_full, "✅ 已开通", "Username", f"@{user.username}"])
                else:
                    results_list.append([p_full, "✅ 已开通", "Tg Data", f"ID: {user.id}"])
            else:
                results_list.append([p_full, "❌ 未开通", "No Tg Data", "-"])

        # --- 3. 保存并发送结果 ---
        output_file = f"checked_{phone}.xlsx"
        df_final = pd.DataFrame(results_list, columns=["原始号码 (+1)", "状态", "分类结果", "详细信息 (Username/ID)"])
        df_final.to_excel(output_file, index=False)
        print(f"[FINISH] {phone} 检查完成，结果已存入 {output_file}")

        try:
            current_date = datetime.now().strftime('%Y-%m-%d')
            await client.send_file(
                "me", 
                output_file, 
                caption=f"📊 检查完成！\n账号: +{phone}\n日期: {current_date}\n总数: {len(results_list)}[cite: 2]"
            )
            print(f"[SENT] 结果文件已成功发送至您的 Telegram 收藏夹")
        except Exception as e:
            print(f"[SEND ERROR] 发送文件失败: {e}")

    await client.disconnect()

async def main():
    # 读取主账号列表[cite: 2]
    accounts_df = pd.read_excel("accounts.xlsx")
    
    for _, account in accounts_df.iterrows():
        phone = normalize_phone(account["phone"])
        contacts_file = f"contacts/{phone}.xlsx"

        if not os.path.exists(contacts_file):
            print(f"[SKIP] {phone} 对应的联系人 Excel 文件不存在")
            continue

        # 强制以字符串格式读取联系人文件，防止长号码变形
        contacts_df = pd.read_excel(contacts_file, dtype={'phone': str})
        await run_account(phone, contacts_df)

        # 任务间歇，保护账号[cite: 2]
        print(f"等待 60 秒后继续下一个账号...")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(main())
