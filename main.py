import os
import pandas as pd
import time
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

# 自动创建 session 文件夹
if not os.path.exists('session'):
    os.makedirs('session')

# 读取账号和联系人
accounts_df = pd.read_excel('accounts.xlsx')
contacts_df = pd.read_excel('contacts.xlsx')

for idx, account in accounts_df.iterrows():
    account_name = account['account_name']
    phone_number = account['phone_number']
    api_id = int(account['api_id'])
    api_hash = account['api_hash']

    print(f"正在登录 {account_name} ({phone_number})...")

    # ✅ 使用 session 登录
    session_path = f'session/{phone_number}.session'  # session 文件名建议手机号
    client = TelegramClient(session_path, api_id, api_hash)
    
    # 不使用交互输入验证码，直接启动 session
    client.start()

    # 过滤属于该账号的联系人
    acc_contacts = contacts_df[contacts_df['account_name'] == account_name]

    contacts = []
    for i, row in acc_contacts.iterrows():
        contacts.append(InputPhoneContact(
            client_id=i,
            phone=row['phone'],
            first_name=row['name'],
            last_name=''
        ))

    # 批量导入联系人
    if contacts:
        client(ImportContactsRequest(contacts))
        print(f"{account_name} 已导入 {len(contacts)} 个联系人")
    else:
        print(f"{account_name} 没有要导入的联系人")

    time.sleep(2)  # 防止 Telegram 风控

print("全部账号导入完成！")
