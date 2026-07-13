import os
import re
import requests

SESSION_TOKEN = os.environ.get("COLLECTR_PASS")

if not SESSION_TOKEN:
    print("❌ Error: No se encontró la cookie en los secretos de GitHub.")
    exit(1)

print("🌐 Conectando a Collectr mediante token de sesión...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Cookie": f"collectrToken={SESSION_TOKEN}"
}

api_url = "https://api.getcollectr.com/api/v1/user/portfolio"

response = requests.get(api_url, headers=headers)

if response.status_code != 200:
    print(f"❌ Error al consultar tus datos. Código: {response.status_code}")
    print("Es probable que tu sesión haya expirado. Intenta copiar una nueva cookie de tu navegador.")
    exit(1)

data = response.json()
items = data.get("items", [])

print(f"🃏 ¡Conexión exitosa con Gmail! Se encontraron {len(items)} cartas en tu cuenta.")

nuevas_cartas = []

nuevas_cartas.append('  { id: 901, name: "Sleeves (Micas Protectoras)", set: "Accesorios", price: 5, stock: 90, sold: false, img: "images.jpg", isSleeve: true, displayPrice: "$5 c/u o 3x$10" }')
nuevas_cartas.append('  { id: 902, name: "Toploader Transparente", set: "Accesorios", price: 10, stock: 98, sold: false, img: "toploader_transparente,jpg.jpg", isToploader: true, displayPrice: "$10 (2x$15)" }')

for index, item in enumerate(items):
    card_id = index + 1
    product = item.get("product", {})
    name = product.get("name", "Carta Pokémon").replace('"', '\\"')
    set_name = product.get("setName", "Expansión")
    
    usd_price = float(product.get("price", 0))
    price = int(usd_price) 
    
    stock = int(item.get("quantity", 1))
    sold = True if stock == 0 else False
    
    img_url = product.get("imageUrl", "")
    if img_url and not img_url.startswith("http"):
        img_url = "https://public.getcollectr.com" + img_url

    formato_html = f'  {{ id: {card_id}, name: "{name}", set: "{set_name}", price: {price}, stock: {stock}, sold: {str(sold).lower()}, img: "{img_url}" }}'
    nuevas_cartas.append(formato_html)

texto_cartas = ",\n".join(nuevas_cartas)

print("📝 Modificando index.html...")
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

pattern = r"const cards = \[\s*// --- BASE DE DATOS DE CARTAS ---.*?\s*\];"
replacement = f"const cards = [\n  // --- BASE DE DATOS DE CARTAS ---\n{texto_cartas}\n];"

nuevo_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(nuevo_html)

print("🚀 ¡Completado con éxito! Tu tienda del Tianguis ya está sincronizada con tus cartas de Gmail.")
