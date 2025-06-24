#!/usr/bin/env python3
"""
Generate product images for Pe Foc de Lemne
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Create images directory if it doesn't exist
images_dir = "../frontend/public/images"
if not os.path.exists(images_dir):
    os.makedirs(images_dir)

# Product data with colors
products = [
    {"filename": "branza-vaca.jpg", "name": "Brânză de vacă", "color": (255, 248, 220), "text_color": (101, 67, 33)},  # Cornsilk
    {"filename": "lapte-ferma.jpg", "name": "Lapte proaspăt", "color": (245, 245, 245), "text_color": (64, 64, 64)},  # WhiteSmoke
    {"filename": "smantana.jpg", "name": "Smântână", "color": (255, 255, 240), "text_color": (139, 90, 43)},  # Ivory
    {"filename": "carnati-casa.jpg", "name": "Cârnați de casă", "color": (139, 69, 19), "text_color": (255, 255, 255)},  # SaddleBrown
    {"filename": "slanina-afumata.jpg", "name": "Slănină afumată", "color": (160, 82, 45), "text_color": (255, 255, 255)},  # Sienna
    {"filename": "rosii-gradina.jpg", "name": "Roșii de grădină", "color": (255, 99, 71), "text_color": (255, 255, 255)},  # Tomato
    {"filename": "mere-ionatan.jpg", "name": "Mere ionatan", "color": (255, 192, 203), "text_color": (139, 0, 0)},  # Pink
    {"filename": "paine-casa.jpg", "name": "Pâine de casă", "color": (222, 184, 135), "text_color": (101, 67, 33)},  # BurlyWood
    {"filename": "cozonac-nuca.jpg", "name": "Cozonac cu nucă", "color": (210, 180, 140), "text_color": (101, 67, 33)},  # Tan
    {"filename": "dulceata-caise.jpg", "name": "Dulceață de caise", "color": (255, 218, 185), "text_color": (210, 105, 30)},  # PeachPuff
    {"filename": "zacusca-vinete.jpg", "name": "Zacuscă de vinete", "color": (128, 0, 128), "text_color": (255, 255, 255)},  # Purple
]

# Create images
for product in products:
    # Create a new image with a background color
    img = Image.new('RGB', (400, 300), color=product["color"])
    draw = ImageDraw.Draw(img)
    
    # Try to use a system font, fallback to default if not available
    try:
        # Try different font sizes and paths
        font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
        small_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
    except:
        try:
            font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 32)
            small_font = ImageFont.truetype("/Library/Fonts/Arial.ttf", 20)
        except:
            # Use default font if system fonts not found
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
    
    # Draw product name
    text = product["name"]
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (400 - text_width) // 2
    y = (300 - text_height) // 2 - 20
    
    # Draw shadow
    draw.text((x+2, y+2), text, font=font, fill=(0, 0, 0, 128))
    # Draw main text
    draw.text((x, y), text, font=font, fill=product["text_color"])
    
    # Add decorative elements
    # Draw border
    draw.rectangle([10, 10, 390, 290], outline=product["text_color"], width=3)
    
    # Add "Produs Local" text
    local_text = "Produs Local"
    bbox = draw.textbbox((0, 0), local_text, font=small_font)
    text_width = bbox[2] - bbox[0]
    x = (400 - text_width) // 2
    y = 250
    draw.text((x, y), local_text, font=small_font, fill=product["text_color"])
    
    # Save the image
    img.save(os.path.join(images_dir, product["filename"]), quality=95)
    print(f"Created: {product['filename']}")

print("\nAll product images created successfully!")