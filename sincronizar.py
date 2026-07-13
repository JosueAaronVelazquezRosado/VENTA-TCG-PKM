import os
import re
import requests

# 1. Traer los secretos guardados en GitHub Actions
EMAIL = os.environ.get("COLLECTR_USER")
PASSWORD = os.environ.get("COLLECTR_PASS")

if not EMAIL or not PASSWORD:
    print("❌ Error: No se configuraron las variables secretas en GitHub.")
    exit(1)

print("🔑 Iniciando sesión simulada en Collectr...")
session = requests.Session()

# Cabeceras estándar para simular un navegador real
headers = {
    "User-Agent": "Mozilla /5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*"
}

# Login en los servidores de Collectr
login_url = "https://api.getcollectr.com/api/v1/auth/login"  
payload = {"email": EMAIL, "password": PASSWORD}

response = session.post(login_url, json=payload, headers=headers)

if response.status_code != 200:
    print("❌ Error de autenticación. Verifica tu correo y contraseña.")
    exit(1)

print("✅ Sesión iniciada con éxito. Extrayendo portafolio...")

# Obtener los artículos de tu colección
# Nota: Cambia el endpoint según la estructura real de su API pública o haz scraping.
portfolio_url = "https://api.getcollectr.com/api/v1/user/portfolio" 
portfolio_data = session.get(portfolio_url, headers=headers).json()

# Procesamos tus cartas al formato exacto que usa tu HTML
nuevas_cartas = []

# Mantenemos tus accesorios manuales intactos primero
nuevas_cartas.append('{ id: 901, name: "Sleeves (Micas Protectoras)", set: "Accesorios", price: 5, stock: 90, sold: false, img: "images.jpg", isSleeve: True, displayPrice: "$5 c/u o 3x$10" }')
nuevas_cartas.append('{ id: 902, name: "Toploader Transparente", set: "Accesorios", price: 10, stock: 98, sold: false, img: "toploader_transparente,jpg.jpg", isToploader: True, displayPrice: "$10 (2x$15)" }')

# Recorremos lo obtenido en Collectr (ajustar llaves del JSON según devuelva su API)
for index, item in enumerate(portfolio_data.get("items", [])):
    card_id = index + 1
    name = item.get("name", "Carta Pokémon")
    set_name = item.get("setName", "Expansión")
    # Convertimos dólares/precios de Collectr a pesos si lo deseas, aquí queda directo:
    price = int(item.get("price", 0)) 
    stock = int(item.get("quantity", 1))
    sold = True if stock == 0 else False
    img_url = item.get("imageUrl", "")

    formato_html = f'  {{ id: {card_id}, name: "{name}", set: "{set_name}", price: {price}, stock: {stock}, sold: {str(sold).lower()}, img: "{img_url}" }}'
    nuevas_cartas.append(formato_html)

texto_cartas = ",\n".join(nuevas_cartas)

# 3. Leer tu index.html e inyectar los nuevos datos de forma automática
print("📝 Actualizando index.html...")
with open("index.html", "r", encoding="utf-8") as f:
    html_content = f.read()

# Buscamos dónde empieza y termina tu lista de cartas usando expresiones regulares
pattern = r"const cards = \[\s*//.*?\s*\];"
replacement = f"const cards = [\n{texto_cartas}\n];"

nuevo_html = re.sub(pattern, replacement, html_content, flags=re.DOTALL)

with open("index.html", "w", encoding="utf-8") as f:
    f.write(nuevo_html)

print("🚀 ¡index.html actualizado exitosamente con tus cartas reales de Collectr!")
