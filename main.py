import asyncio
from config import *
from telethon import TelegramClient, events, Button
from telethon.tl.types import InputPeerChat

status = ""
response_id = ""

buttons_cancel = [
    [
        Button.text("انصراف 🫠", resize=True, single_use=True),
    ],
]


async def add_statistics(the_user_id):
    global sqliteConnection
    import sqlite3

    try:
        # Connect to DB and create a cursor
        sqliteConnection = sqlite3.connect('database.db')
        cursor = sqliteConnection.cursor()
        print('DB Init')

        # Write a query and execute it with cursor
        # query = 'select sqlite_version();'
        cursor.execute(f"select add_statistics from statistics where user_id = '{the_user_id}'")
        old_val = cursor.fetchall()
        print("old_val:", old_val)
        if not old_val:
            cursor.execute(f'insert into statistics (user_id, add_statistics) values ({the_user_id}, 1);')
            sqliteConnection.commit()
            print(f"user {the_user_id} inserted")
        else:
            for i in old_val:
                new_val = int(i[0]) + 1
                cursor.execute(f'update statistics set add_statistics = {new_val} where user_id = {the_user_id};')
                sqliteConnection.commit()

        cursor.close()

        #
        # try:
        #     # Fetch and output result
        #     result = cursor.fetchall()
        #     print('SQLite Version is {}'.format(result))
        # except sqlite3.Error as error:
        #     print('error dad {}'.format(error))


        # Close the cursor
        cursor.close()

    # Handle errors
    except sqlite3.Error as error:
        print('Error occurred - ', error)

    # Close DB Connection irrespective of success
    # or failure
    finally:
        if sqliteConnection:
            sqliteConnection.close()
            print('SQLite Connection closed')


async def message_handler(event):
    global status
    buttons = [
        [
            # Button.inline("حمایت از ما 💰", "donate"),
            Button.inline(" 💌 درخواست همکاری", "hamkari")
        ],
        [
            # Button.inline("دریافت VPN رایگان", "vpn")
            Button.inline(" 👊 معرفی پیج یا پست برای ریپورت", "report"),
            Button.inline(" ⚔️ شرکت در عملیات", "join"),
            # Button.inline("ثبت بازخورد و عملیات", "review")
        ],
        # [
        #     Button.inline(" 💌 ارتباط با ما", "contact")
        # ],
    ]

    print(event)
    msg = event.message.message
    print(msg)

    print("chat.id: ", event.chat.id, event.sender_id)

    if event.message.is_reply and event.chat.id in AdminsDic:
        reply = await event.get_reply_message()
        chat_reply = InputPeerChat(reply)
        reply_peer_id = chat_reply.chat_id.forward.from_id.user_id
        print('Reply')
        print("reply.id", reply.id)
        print("reply", reply)
        print("entity", event.message.reply_to)
        print("reply_to", event.message.reply_to.reply_to_msg_id)
        print("chat1", chat_reply)
        print("reply_peer_id", reply_peer_id)

        await event.client.send_message(
            entity=reply_peer_id,
            message=f"ادمین به پیام شما پاسخ داد🔽🔽🔽\n\n\n{msg}",
            reply_to=reply.id,
            file=event.message.media,
        )
        await reply.reply("پیامت بهش رسید")

    try:
        if not hasattr(event.chat, "last_name"):
            user_full_name = event.chat.first_name
        else:
            user_full_name = f"{event.chat.first_name} {event.chat.last_name}"
    except AttributeError:
        user_full_name = ""
        print(AttributeError)

    if msg == "/start" or msg == "انصراف 🫠":
        await event.client.send_message(
            event.chat_id,
            "\n به ربات **قرارگاه سایبری ابالفضل (ع)** خوش آمدید \n 🇮🇷🇮🇷🇮🇷️"
            .format(event.chat.first_name),
            file="assets/icon.jpg",
            buttons=buttons,
        )
        await send_msg_to_admin(
            msg_type="send",
            event=event,
            file=await event.client.download_profile_photo(event.sender_id),
            text="عضو جدید در ربات: \n\n"
                 "⭕ ID: [{uid}](tg://user?id={uid}) \n\n"
                 "⭕ Name: [{name}](tg://user?id={uid}) \n\n"
                 "⭕ UserName: [@{username}](https://t.me/{username}) \n\n"
                 "⭕ Tel: [{phone}](https://t.me/{phone}) \n\n".format(
                uid=event.chat.id,
                name=user_full_name,
                username=event.chat.username,
                phone=event.chat.phone,
            ),
        )
    elif msg == "/hamkari":
        await hamkari_trigger(event)
    elif msg == "/report":
        await report_trigger(event)
    elif msg == "/join":
        await join_trigger(event)
    # elif msg == "/review":
    #     await review_trigger(event)
    elif msg == "/contact":
        await contact_trigger(event)
    else:
        if event.is_group:
            if event.message.from_id.user_id not in AdminsDic:
                await event.delete()
        else:
            reply_btn = [
                [
                    Button.inline("🤪پاسخ به این پیام", f"response_{event.chat.id}"),
                    Button.inline("⛔ بلاک 🚫", f"block_{event.chat.id}"),
                ],
            ]
            await send_msg_to_admin(
                msg_type="forward",
                event=event,
            )
            await send_msg_to_admin(
                msg_type="send",
                event=event,
                text="پیام از: \n\n"
                     "⭕ PeerID: [{uid}](tg://user?id={uid}) \n\n"
                     "⭕ Name: [{name}](tg://user?id={uid}) \n\n"
                     "⭕ UserName: [@{username}](https://t.me/{username}) \n\n"
                     "⭕ Tel: [{phone}](https://t.me/{phone}) \n\n\n\n"
                     "Text:\n\n `{text}`".format(
                    uid=event.chat.id,
                    name=user_full_name,
                    username=event.chat.username,
                    phone=event.chat.phone,
                    text=msg,
                ),
                file=event.message.media,
                btn=reply_btn,
            )
            status = None
            if status == "report":
                await event.client.forward_messages(AdminID, event.message)
            elif status == "hamkari":
                await event.client.forward_messages(AdminID, event.message)
            # elif status == "join":
            #     await event.reply(" با تشکر از حمایت شما \n به امید پیروزی \n ✌️✌️✌️")
            elif status == "replying":
                await event.client.send_message(
                    response_id,
                    f"ادمین به پیام شما پاسخ داد🔽🔽🔽\n\n\n{msg}",
                    buttons=Button.clear()
                )
            else:
                await event.client.send_message(
                    event.chat_id,
                    " با تشکر از پیام شما \n به امید سربازی در رکاب امام زمان (عج) \n ✌🇮🇷",
                    buttons=Button.clear()
                )


async def chat_handler(event):
    if event.user_joined:
        await event.delete()
    elif event.user_added:
        await add_statistics(event.added_by.id)
        await event.delete()
        # await event.client.send_message(
        #     event.chat_id,
        #     "خوش اومدی به گروه",
        #     buttons=Button.clear()
        # )
        # await event.replay("خوش اومدی به گروه")
    elif event.user_left or event.user_kicked:
        # await event.replay("برو دست خدای مهربون")
        await event.delete()
    else:
        if event.chat.id not in AdminsDic:
            await event.delete()


async def inline_handler(event):
    btn_msg = event.data.decode()
    print(btn_msg)
    if btn_msg == "report":
        await report_trigger(event)
    elif btn_msg == "hamkari":
        await hamkari_trigger(event)
    elif btn_msg == "join":
        await join_trigger(event)
    elif btn_msg == "contact":
        await contact_trigger(event)
    elif btn_msg.startswith("response_"):

        sender_user_id = str(btn_msg).replace("response_", "")
        if event.chat.id in AdminsDic:
            await event.answer("شما مدیر هستید")
        else:
            await event.answer("فقط مدیرا میتونن این کارو بکنن")

        await event.client.send_message(
            event.chat_id,
            f'در حال پاسخ به {sender_user_id}',
            buttons=[
                [
                    Button.text(text="لغو ارسال پیام", resize=True, single_use=True)
                ]
            ]
        )

        global status, response_id
        status = "replying"
        response_id = sender_user_id

    else:
        await event.answer('پاسخ غلطههههههههه', alert=True)


async def report_trigger(e):
    if hasattr(e, 'answer'):
        await e.answer(' 👀 لطفا لینک یا آیدی را برای ریپورت بنویسید \n یا اینجا فوروارد کنید', )
    await e.client.send_message(
        e.chat_id,
        " 👀 لطفا لینک یا آیدی را برای ریپورت بنویسید \n یا اینجا فوروارد کنید",
        buttons=buttons_cancel
    )
    global status
    status = "report"


async def hamkari_trigger(e):
    if hasattr(e, 'answer'):
        await e.answer('برای همکاری با ما **تخصص** و نوع همکاری که به آن علاقه مند هستید را بنویسید', )
    await e.client.send_message(
        e.chat_id,
        "برای همکاری با ما \n اول توی کانال عضو بشید \n و بعدش **تخصص** "
        "\n و **نوع همکاری** \n که به آن علاقه مند هستید را \n  بنویسید \n "
        "[عضویت در کانال](https://t.me/Abolfazl_Cyber_Army)\n ",
        buttons=[
            [
                Button.request_phone(
                    "اگه دوست داشتین شماره تماستونو با این دکمه برامون بفرستید",
                    resize=True,
                    single_use=True
                )
            ]
        ]
    )
    global status
    status = "hamkari"


async def join_trigger(e):
    if hasattr(e, 'answer'):
        await e.answer(' 👀  برای شرکت در عملیات ها اطلاعات تماس خود را با ما به اشتراک بگذارید \n '
                       'تا دسترسی به گروه به شما داده شود',
                       )
    await e.client.send_message(
        e.chat_id,
        ' 👀  برای شرکت در عملیات ها اطلاعات تماس خود را با ما به اشتراک بگذارید \n '
        'تا دسترسی به گروه به شما داده شود',
        buttons=buttons_cancel
    )
    global status
    status = "report"


async def contact_trigger(e):
    await e.client.send_message(
        e.chat_id,
        "🌐 سایت: [Iran-Onlin.IR](http://iran-onlin.ir) \n\n"
        "⭕ کانال: [تلگرام](https://t.me/Abolfazl_Cyber_Army) \n\n"
        "⏺ گروه : [تلگرام](https://t.me/+dNbbp68BIZtjYWU8) \n\n",
        buttons=Button.clear(),
        file="assets/icon.jpg",
        link_preview=False,
    )
    global status
    status = "contact"


async def send_msg_to_admin(event, msg_type, file="", text="", btn=Button.clear()):
    # for admin in AdminsDic:
    if msg_type == "forward":
        await event.client.forward_messages(AdminID, event.message)  # Forward all input messages to admin
    else:
        await event.client.send_message(
            AdminID,
            text,
            file=file,
            buttons=btn
        )


async def main():
    client = TelegramClient("userBot", API_ID, API_HASH)
    await client.start(bot_token=TOKEN)
    # client.add_event_handler(command_message_handler, events.NewMessage(pattern="[^/].+"))  # just commands
    client.add_event_handler(chat_handler, events.ChatAction())
    client.add_event_handler(message_handler, events.NewMessage())
    client.add_event_handler(inline_handler, events.CallbackQuery())
    await client.run_until_disconnected()


asyncio.run(main())
