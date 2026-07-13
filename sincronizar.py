import os
import re
import requests

SESSION_TOKEN = os.environ.get("COLLECTR_PASS")

if not SESSION_TOKEN:
    print("❌ Error: No se encontró la cookie en los secretos de GitHub.")
    exit(1)

print("🌐 Conectando a Collectr mediante la ruta interna de datos...")

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Cookie": f"collectrToken={SESSION_TOKEN}"
}

# 🛠️ NUEVA RUTA: Apunta al endpoint de datos internos que carga tu portafolio
api_url = "https://app.getcollectr.com/api/portfolio"

response = requests.get(api_url, headers=headers)

# Si esa ruta corta tampoco responde, probamos con la ruta de la colección principal
if response.status_code == 404:
    print("🔄 Intentando ruta alternativa de colección...")
    api_url = "https://app.getcollectr.com/api/collection"
    response = requests.get(api_url, headers=headers)

if response.status_code != 200:
    print(f"❌ Error al consultar tus datos. Código: {response.status_code}")
    print("Si da 401 o 403, tu cookie collectrToken copiada expiró o está incompleta.")
    exit(1)

data = response.json()

# Buscamos la lista de cartas dentro de la respuesta
# Dependiendo del formato, puede venir directo o dentro de 'portfolio' / 'collection'
items = data.get("items", data.get("portfolio", {}).get("items", data.get("collection", {}).get("items", [])))

print(f"🃏 ¡Conexión exitosa! Se encontraron {len(items)} cartas en tu cuenta.")

nuevas_cartas = []

# Mantener tus accesorios fijos intactos
nuevas_cartas.append('  { id: 901, name: "Sleeves (Micas Protectoras)", set: "Accesorios", price: 5, stock: 90, sold: false, img: "images.jpg", isSleeve: true, displayPrice: "$5 c/u o 3x$10" }')
nuevas_cartas.append('  { id: 902, name: "Toploader Transparente", set: "Accesorios", price: 10, stock: 98, sold: false, img: "toploader_transparente,jpg.jpg", isToploader: true, displayPrice: "$10 (2x$15)" }')

for index, item in enumerate(items):
    card_id = index + 1
    product = item.get("product", item)
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

print("🚀 ¡Completado con éxito!")
