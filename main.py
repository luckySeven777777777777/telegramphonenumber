from telethon import TelegramClient
from telethon.tl.functions.contacts import ImportContactsRequest
from telethon.tl.types import InputPhoneContact
import pandas as pd
import os
import asyncio

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH")

def normalize_phone(phone):
    return "".join(filter(str.isdigit, str(phone)))

accounts_df = pd.read_excel("accounts.xlsx")

async def run_account(phone, contacts_df):
    session = f"sessions/{phone}"
    client = TelegramClient(session, API_ID, API_HASH)

    await client.connect()

    if not await client.is_user_authorized():
        print(f"[SKIP] {phone} session 不存在")
        await client.disconnect()
        return

    contacts = []
    for _, row in contacts_df.iterrows():
        contact_phone = normalize_phone(row["phone"])
        contacts.append(InputPhoneContact(
            client_id=0,
            phone=contact_phone,
            first_name=str(row.get("name", "")).strip(),
            last_name=""
        ))

    if contacts:
        await client(ImportContactsRequest(contacts))
        print(f"[OK] {phone} 导入 {len(contacts)} 个联系人")

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
        await asyncio.sleep(60)

asyncio.run(main())
