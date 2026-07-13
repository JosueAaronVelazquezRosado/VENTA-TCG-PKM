import os
import re
import requests
from bs4 import BeautifulSoup
import json

# 🫵 REEMPLAZA ESTA URL POR TU ENLACE PÚBLICO DE COLLECTR:
URL_PUBLICAS_COLLECTR = "https://app.getcollectr.com/portfolio/products"

print("🌐 Conectando con tu portafolio público de Collectr...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

response = requests.get(URL_PUBLICAS_COLLECTR, headers=headers)

if response.status_code != 200:
    print(f"❌ No se pudo acceder a la página. Código de estado: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.text, 'html.parser')

# Buscamos el estado de la aplicación donde Collectr inyecta los datos de las cartas
script_tag = soup.find('script', id='__NEXT_DATA__')

nuevas_cartas = []

# Mantenemos tus accesorios manuales intactos al inicio
nuevas_cartas.append('  { id: 901, name: "Sleeves (Micas Protectoras)", set: "Accesorios", price: 5, stock: 90, sold: false, img: "images.jpg", isSleeve: true, displayPrice: "$5 c/u o 3x$10" }')
nuevas_cartas.append('  { id: 902, name: "Toploader Transparente", set: "Accesorios", price: 10, stock: 98, sold: false, img: "toploader_transparente,jpg.jpg", isToploader: true, displayPrice: "$10 (2x$15)" }')

if script_tag:
    try:
        data = json.loads(script_tag.string)
        # Extraemos la lista de cartas directamente del JSON interno que renderiza la web
        items = data.get('props', {}).get('pageProps', {}).get('showcase', {}).get('items', [])
        
        print(f"🃏 Se encontraron {len(items)} cartas en tu Collectr. Procesando...")
        
        for index, item in enumerate(items):
            card_id = index + 1
            # Adaptamos los campos según la estructura nativa del JSON de Collectr
            name = item.get('product', {}).get('name', 'Carta Pokémon').replace('"', '\\"')
            set_name = item.get('product', {}).get('setName', 'Expansión')
            
            # Si el precio viene en USD, lo dejamos base o multiplicamos por tipo de cambio aproximado
            usd_price = float(item.get('product', {}).get('price', 0))
            price = int(usd_price)  # Puedes ajustarlo si calculas MXN automáticos
            
            stock = int(item.get('quantity', 1))
            sold = True if stock == 0 else False
            
            # Conseguimos la imagen optimizada
            img_url = item.get('product', {}).get('imageUrl', '')
            if img_url and not img_url.startswith('http'):
                img_url = "https://public.getcollectr.com" + img_url

            formato_html = f'  {{ id: {card_id}, name: "{name}", set: "{set_name}", price: {price}, stock: {stock}, sold: {str(sold).lower()}, img: "{img_url}" }}'
            nuevas_cartas.append(formato_html)
            
    except Exception as e:
        print(f"❌ Error al procesar los datos estructurados: {e}")
        exit(1)
else:
    print("❌ No se encontró el tag de datos. Intentando método alternativo...")
    exit(1)

texto_cartas = ",\n".join(nuevas_cartas)

# 3. Reescribir el index.html
print("📝 Actualizando tu index.html...")
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

pattern = r"const cards = \[\s*// --- BASE DE DATOS DE CARTAS ---.*?\s*\];"
replacement = f"const cards = [\n  // --- BASE DE DATOS DE CARTAS ---\n{texto_cartas}\n];"

nuevo_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(nuevo_html)

print("🚀 ¡Tu web se ha sincronizado correctamente con tu escaparate público!")
