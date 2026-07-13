import json
import re

print("📦 VERSIÓN NUEVA: Leyendo datos locales desde cartas.json...")

try:
    with open("cartas.json", "r", encoding="utf-8") as f:
        data = json.load(f)
except Exception as e:
    print(f"❌ Error al leer cartas.json: {e}")
    exit(1)

# En Collectr a veces los datos vienen en una lista directa o dentro de un objeto
items = data if isinstance(data, list) else data.get("items", [])
print(f"🃏 ¡Datos leídos con éxito! Se encontraron {len(items)} cartas guardadas.")

nuevas_cartas = []

# Tus accesorios fijos
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

print("🚀 ¡Completado con éxito! Tu index.html se ha actualizado usando los datos guardados.")
