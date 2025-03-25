import os
import uuid
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from transformers import pipeline
from googletrans import Translator
from PIL import Image
from django.conf import settings
from playwright.async_api import async_playwright
import logging
from langdetect import detect
import urllib.parse
from bs4 import BeautifulSoup
import io


logger = logging.getLogger('pricep')

blip_model = None

def check_api_key(request):
    return request.headers.get("X-API-Key") == getattr(settings, "API_KEY", None)

def prepare_text(text):
    return text.lower().strip()

def init_blip_model():
    global blip_model
    if blip_model is None:
        blip_model = pipeline(
            "image-to-text",
            model="Salesforce/blip-image-captioning-base",
            use_fast=True
        )
        logger.info("Blip model initialized.")
    return blip_model

init_blip_model()

def decode_picture(image_data, pipe):
    if pipe is None:
        logger.error("Blip model is not initialized.")
        return False, "Model is not initialized."

    logger.info("Processing image from memory")
    try:
        image = Image.open(image_data)
        result = pipe(image)
        generated_text = result[0]['generated_text']
        logger.info(f"Image description: {generated_text}")
        return True, generated_text
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return False, f"Error processing image: {str(e)}"
    


async def fetch_html_page(search_query):
    encoded_query = urllib.parse.quote(search_query)
    url = f"https://ozon.by/search/?text={encoded_query}"
    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=True,
            args=["--disable-extensions", "--disable-gpu", "--no-sandbox"]
        )
        page = await browser.new_page()
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined});")
        async def block_requests(route, request):
            if request.resource_type in ["image", "stylesheet", "font"]:
                await route.abort()
            else:
                await route.continue_()
        page.on("route", block_requests)
        await page.goto(url)
        await page.wait_for_selector("div[class*=tile-root]", timeout=15000)
        html_content = await page.content()
        await browser.close()
    return html_content, url  # Возвращаем и ссылку на страницу

async def find_product_by_data_index(html_content, num_results=8):
    soup = BeautifulSoup(html_content, "html.parser")
    products = []
    for product_card in soup.find_all("div", {"data-index": True}):
        # Извлекаем цену
        price_tag = product_card.find("span", class_="c3025-a1")
        if not price_tag:
            continue

        # Извлекаем название товара
        name_tag = product_card.find("span", class_="tsBody500Medium")
        name = name_tag.text.strip() if name_tag else "Без названия"

        link_tag = product_card.find("a", href=True)
        link = "https://ozon.by" + link_tag["href"] if link_tag else None

        product_info = {
            "name": name,
            "price": price_tag.text.strip().replace("\u2009", " "),
            "url": link
        }

        products.append(product_info)
        if len(products) >= num_results:
            break

    return {
        "status": "success" if products else "warn",
        "products": products
    }


@csrf_exempt
async def text_search_view(request):
    if not check_api_key(request):
        return JsonResponse({'error': 'Invalid API Key'}, status=403)

    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request'}, status=400)

    try:
        data = json.loads(request.body)
        input_text = data.get('q')
        if not input_text:
            return JsonResponse({'error': 'q not provided'}, status=400)

        detected_language = detect(input_text)
        translator = Translator()
        result_text = input_text if detected_language == 'ru' else translator.translate(prepare_text(input_text), src="en", dest="ru").text

        html_content, main_url = await fetch_html_page(result_text)
        products = await find_product_by_data_index(html_content, 5)

        # Возвращаем главную ссылку
        return JsonResponse({
            'answer_text': result_text,
            'product_info': products['products'],
            'main_url': main_url  # Добавляем главную ссылку
        })
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    


@csrf_exempt
async def image_search_view(request):
    if not check_api_key(request):
        return JsonResponse({'error': 'Invalid API Key'}, status=403)
    
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    image_file = request.FILES['image']

    # Создаем временный файл в памяти
    image_data = io.BytesIO()
    for chunk in image_file.chunks():
        image_data.write(chunk)
    image_data.seek(0)  # Перемещаем указатель в начало файла

    translator = Translator()
    logger.info("Processing uploaded image")
    
    # Передаем данные изображения в decode_picture
    status, result_text = decode_picture(image_data, blip_model)

    if not status:
        return JsonResponse({'error': result_text}, status=400)

    translated_text = translator.translate(prepare_text(result_text), src="en", dest="ru").text

    # Асинхронный вызов поиска товара
    html_content, main_url = await fetch_html_page(translated_text)
    products = await find_product_by_data_index(html_content, 5)

    return JsonResponse({
        'answer_text': translated_text,
        'product_info': products['products'],
        'main_url': main_url  # Добавляем главную ссылку
    })


@csrf_exempt
async def define_image(request):
    if not check_api_key(request):
        return JsonResponse({'error': 'Invalid API Key'}, status=403)
    
    if request.method != 'POST' or 'image' not in request.FILES:
        return JsonResponse({'error': 'Invalid request'}, status=400)

    image_file = request.FILES['image']

    # Создаем временный файл в памяти
    image_data = io.BytesIO()
    for chunk in image_file.chunks():
        image_data.write(chunk)
    image_data.seek(0)  # Перемещаем указатель в начало файла

    translator = Translator()
    logger.info("Processing uploaded image")
    
    # Передаем данные изображения в decode_picture
    status, result_text = decode_picture(image_data, blip_model)

    if not status:
        return JsonResponse({'error': result_text}, status=400)

    translated_text = translator.translate(prepare_text(result_text), src="en", dest="ru").text
    
    return JsonResponse({
        'answer_text': translated_text,
    })
