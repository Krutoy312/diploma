import asyncio
from os import getenv
from django.shortcuts import render
from g4f.client import Client
from telethon import TelegramClient


API_ID = getenv('SECRET_API_ID')
API_HASH = getenv('SECRET_API_HASH')
PHONE_NUMBER = getenv('SECRET_PHONE_NUMBER')
chanel = "https://t.me/+f25H8sQrMfc1Zjli"
loop = asyncio.new_event_loop()

client = TelegramClient("session_name", API_ID, API_HASH)

def run_async_function(async_func, *args):
    """Создаёт и запускает новый event loop в отдельном потоке"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(async_func(*args))
    loop.close()
    return result

async def send_telegram_post(text_to_send, media_paths):
    await client.connect()

    if not await client.is_user_authorized():
        await client.send_code_request(PHONE_NUMBER)
        code = input("Введите код из Telegram: ")  # Вводим код вручную при первом pзапуске
        await client.sign_in(PHONE_NUMBER, code)
    if media_paths:
        await client.send_file(chanel, media_paths, caption=text_to_send)
    else:
        await client.send_message(chanel, text_to_send)

def post_form_view(request):
    if request.method == "POST":
        if "generate" in request.POST:
            client_gpt = Client()
            response = client_gpt.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": request.POST.get('generate_text')}],
                web_search=False
            )
            return render(request, 'post/index.html', {'generated_text':response.choices[0].message.content})
        elif "send" in request.POST:  # Обработка отправки поста
            manual_text = request.POST.get("manual_text", "")
            media_files = request.FILES.getlist("media")
            platforms = request.POST.getlist("platforms")

            if "telegram" in platforms:
                asyncio.set_event_loop(loop)
                loop.run_until_complete(send_telegram_post(manual_text, media_files))


    return render(request, 'post/index.html')

