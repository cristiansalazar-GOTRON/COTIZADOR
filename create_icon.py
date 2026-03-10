from PIL import Image, ImageDraw
import struct
import io

# Crear una imagen PNG de alta calidad
size = 256
image = Image.new('RGBA', (size, size), (200, 220, 240, 255))  # Fondo azul claro
draw = ImageDraw.Draw(image)

# Colores mejorados
gray = (130, 140, 155, 255)
blue_dark = (20, 60, 140, 255)
blue_medium = (50, 110, 180, 255)
blue_light = (100, 160, 220, 255)
white = (255, 255, 255, 255)

center_x, center_y = size // 2, size // 2

# Sombra del caracol (efecto 3D) - AMPLIADA
shadow_color = (100, 100, 100, 80)
for i in range(3):
    offset = (i + 1) * 2
    r = 130 - (i * 10)
    draw.ellipse(
        [(center_x - r + offset, center_y + 40 + offset),
         (center_x + r + offset, center_y + 160 + offset)],
        fill=shadow_color
    )

# Espiral/caracol - núcleo central (grandes círculos) - AMPLIADA
draw.ellipse([(center_x - 110, center_y - 110), (center_x + 110, center_y + 110)], 
             fill=blue_light, outline=blue_dark, width=3)

draw.ellipse([(center_x - 90, center_y - 90), (center_x + 90, center_y + 90)], 
             fill=blue_medium, outline=blue_dark, width=3)

draw.ellipse([(center_x - 70, center_y - 70), (center_x + 70, center_y + 70)], 
             fill=blue_light, outline=blue_dark, width=3)

draw.ellipse([(center_x - 50, center_y - 50), (center_x + 50, center_y + 50)], 
             fill=blue_dark, outline=white, width=3)

# Centro de la espiral - MÁS GRANDE
draw.ellipse([(center_x - 24, center_y - 24), (center_x + 24, center_y + 24)], 
             fill=white, outline=blue_dark, width=2)

# Cuerpo del caracol (abajo) - AMPLIADO
body_x = center_x
body_y = center_y + 100
body_width, body_height = 100, 130

# Cuerpo redondeado
draw.rounded_rectangle(
    [(body_x - body_width//2, body_y),
     (body_x + body_width//2, body_y + body_height)],
    radius=40,
    fill=gray,
    outline=blue_dark,
    width=3
)

# Cabeza del caracol - AMPLIADA
head_y = body_y + body_height
head_radius = 40
draw.ellipse(
    [(body_x - head_radius, head_y - 10),
     (body_x + head_radius, head_y + head_radius + 30)],
    fill=gray,
    outline=blue_dark,
    width=3
)

# Ojos - MÁS GRANDES
eye_y = head_y + 20
eye_radius = 12
draw.ellipse([(body_x - 28, eye_y), (body_x - 28 + eye_radius * 2, eye_y + eye_radius * 2)],
             fill=blue_dark)
draw.ellipse([(body_x + 16, eye_y), (body_x + 16 + eye_radius * 2, eye_y + eye_radius * 2)],
             fill=blue_dark)

# Brillos en los ojos - MÁS GRANDES
draw.ellipse([(body_x - 24, eye_y + 4), (body_x - 20, eye_y + 8)], fill=white)
draw.ellipse([(body_x + 20, eye_y + 4), (body_x + 24, eye_y + 8)], fill=white)

# Antenas - MÁS GRANDES
antenna_base = head_y - 20
antenna_top = head_y - 70
draw.line([(body_x - 24, antenna_base), (body_x - 40, antenna_top)], fill=blue_dark, width=8)
draw.line([(body_x + 24, antenna_base), (body_x + 40, antenna_top)], fill=blue_dark, width=8)

# Bolitas en las antenas - MÁS GRANDES
antenna_ball_r = 10
draw.ellipse([(body_x - 44, antenna_top - antenna_ball_r), 
              (body_x - 44 + antenna_ball_r * 2, antenna_top + antenna_ball_r)],
             fill=blue_light, outline=blue_dark, width=3)
draw.ellipse([(body_x + 36, antenna_top - antenna_ball_r), 
              (body_x + 36 + antenna_ball_r * 2, antenna_top + antenna_ball_r)],
             fill=blue_light, outline=blue_dark, width=3)

# Guardar como PNG primero
image.save('cotizador_temp.png', 'PNG')

# Convertir PNG a ICO con múltiples tamaños
def create_ico_from_image(png_path, ico_path):
    base_image = Image.open(png_path)
    
    # Crear versiones en diferentes tamaños para ICO
    sizes = [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)]
    images = []
    
    for size in sizes:
        resized = base_image.resize(size, Image.LANCZOS)
        images.append(resized)
    
    # Guardar como ICO
    images[0].save(ico_path, format='ICO', sizes=sizes)

create_ico_from_image('cotizador_temp.png', 'cotizador.ico')

print("✓ Icono ampliado creado: cotizador.ico")

# Limpiar archivo temporal
import os
os.remove('cotizador_temp.png')
