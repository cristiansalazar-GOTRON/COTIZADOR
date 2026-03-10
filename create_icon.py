from PIL import Image, ImageDraw
import math

# Crear una imagen con fondo transparente
size = 256
image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
draw = ImageDraw.Draw(image)

# Colores
gray = (150, 160, 170, 255)
blue_dark = (30, 80, 150, 255)
blue_light = (70, 130, 200, 255)
white = (255, 255, 255, 255)

# Centro
center_x, center_y = size // 2, size // 2

# Dibujar el caracol - espiral
# Cuerpo principal (círculos concéntricos)
for i in range(5, 0, -1):
    radius = 50 - (i * 8)
    color = blue_light if i % 2 == 0 else blue_dark
    draw.ellipse(
        [(center_x - radius, center_y - radius), 
         (center_x + radius, center_y + radius)],
        fill=color,
        outline=gray
    )

# Cuerpo alargado (parte inferior)
body_width = 45
body_height = 60
draw.rounded_rectangle(
    [(center_x - body_width//2, center_y + 20),
     (center_x + body_width//2, center_y + body_height)],
    radius=15,
    fill=gray,
    outline=blue_dark
)

# Cabeza del caracol
head_radius = 18
draw.ellipse(
    [(center_x - head_radius, center_y + body_height - 10),
     (center_x + head_radius, center_y + body_height + 26)],
    fill=gray,
    outline=blue_dark
)

# Ojos
eye_radius = 4
eye_y = center_y + body_height + 8
draw.ellipse(
    [(center_x - 12, eye_y), (center_x - 12 + eye_radius * 2, eye_y + eye_radius * 2)],
    fill=blue_dark
)
draw.ellipse(
    [(center_x + 8, eye_y), (center_x + 8 + eye_radius * 2, eye_y + eye_radius * 2)],
    fill=blue_dark
)

# Pequeños círculos blancos en los ojos
draw.ellipse(
    [(center_x - 10, eye_y + 1), (center_x - 8, eye_y + 3)],
    fill=white
)
draw.ellipse(
    [(center_x + 10, eye_y + 1), (center_x + 12, eye_y + 3)],
    fill=white
)

# Antenas del caracol
antenna_start_y = center_y + body_height + 5
antenna_top_y = center_y + body_height - 30
draw.line([(center_x - 10, antenna_start_y), (center_x - 15, antenna_top_y)], fill=blue_dark, width=3)
draw.line([(center_x + 10, antenna_start_y), (center_x + 15, antenna_top_y)], fill=blue_dark, width=3)

# Bordes pequeños en las antenas
draw.ellipse([(center_x - 17, antenna_top_y - 4), (center_x - 13, antenna_top_y)], fill=blue_light)
draw.ellipse([(center_x + 13, antenna_top_y - 4), (center_x + 17, antenna_top_y)], fill=blue_light)

# Guardar como .ico
image.save('cotizador.ico')
print("✓ Icono creado: cotizador.ico")
