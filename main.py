import os
import pandas as pd
import time
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact

if not os.path.exists('session'):
    os.makedirs('session')

accounts_df = pd.read_excel('accounts.xlsx')
contacts_df = pd.read_excel('contacts.xlsx')

for idx, account in accounts_df.iterrows():
    account_name = account['account_name']
    phone_number = account['phone_number']
    api_id = int(account['api_id'])
    api_hash = account['api_hash']

    print(f"正在登录 {account_name} ({phone_number})...")
    client = TelegramClient(f'session/{phone_number}', api_id, api_hash)
    client.start(phone=phone_number)

    acc_contacts = contacts_df[contacts_df['account_name'] == account_name]

    contacts = []
    for i, row in acc_contacts.iterrows():
        contacts.append(InputPhoneContact(client_id=i, phone=row['phone'], first_name=row['name'], last_name=''))

    if contacts:
        client(ImportContactsRequest(contacts))
        print(f"{account_name} 已导入 {len(contacts)} 个联系人")
    else:
        print(f"{account_name} 没有要导入的联系人")

    time.sleep(2)

print("全部账号导入完成！")
