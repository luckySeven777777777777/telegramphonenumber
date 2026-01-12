
from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import pandas as pd
import os
import time

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

accounts_df = pd.read_excel("accounts.xlsx")
os.makedirs("sessions", exist_ok=True)

for _, account in accounts_df.iterrows():
    phone = str(account['phone'])
    contacts_file = f"contacts/{phone}.xlsx"

    if not os.path.exists(contacts_file):
        print(f"[SKIP] {phone} 没有对应联系人文件")
        continue

    contacts_df = pd.read_excel(contacts_file)
    session = f"sessions/{phone}"

    with TelegramClient(session, API_ID, API_HASH) as client:
        contacts = []
        for _, row in contacts_df.iterrows():
            contacts.append(InputPhoneContact(
                client_id=0,
                phone=str(row['phone']),
                first_name=str(row.get('name', '')),
                last_name=""
            ))

        if contacts:
            client(ImportContactsRequest(contacts))
            print(f"[OK] {phone} 导入 {len(contacts)} 个联系人")

    time.sleep(60)
