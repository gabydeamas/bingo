import random
import textwrap
import re
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import json
# ============================================================
# CONFIGURACIÓN
# ============================================================
ARCHIVO_CANCIONES = "canciones_bingo.txt"
DIMENSION = 5
CENTRO_LIBRE = False
NUM_CARTONES = 20
NOMBRE_PDF = "cartones_bingo.pdf"
TITULO = "🎵 BINGO MUSICAL"
FUENTE = "Helvetica"
FUENTE_TITULO = "Helvetica-Bold"
TAMANO_TITULO = 16
MARGEN_CELDA = 0.05 * cm
RADIO_REDONDEO = 12

# Colores
COLOR_FONDO_CARTON = (0.98, 0.98, 0.98)
COLOR_BORDE_CARTON = (0.1, 0.1, 0.3)
COLOR_BORDE_CELDA = (0.2, 0.2, 0.4)
COLOR_CELDA_IMPAR = (0.96, 0.96, 1.0)
COLOR_CELDA_PAR = (0.90, 0.90, 0.98)
COLOR_TITULO = (0.0, 0.2, 0.6)
COLOR_TEXTO = (0, 0, 0)
# ============================================================


def guardar_json(cartones, archivo="cartones.json"):
    """Guarda los cartones en un archivo JSON para la web."""
    # Convertir None a null para JSON
    datos = []
    for carton in cartones:
        datos.append([c if c is not None else None for c in carton])
    with open(archivo, "w", encoding="utf-8") as f:
        json.dump(datos, f, ensure_ascii=False, indent=2)
    print(f"✅ Datos guardados en {archivo}")
def leer_canciones(archivo):
    try:
        with open(archivo, 'r', encoding='utf-8') as f:
            lineas = [l.strip() for l in f if l.strip()]
        canciones = []
        for linea in lineas:
            limpia = re.sub(r'\([^)]*\)', '', linea)
            limpia = re.sub(r'\[[^\]]*\]', '', limpia)
            if ' - ' in limpia:
                limpia = limpia.split(' - ')[0].strip()
            elif '–' in limpia:
                limpia = limpia.split('–')[0].strip()
            canciones.append(limpia if limpia else linea)
        canciones = list(dict.fromkeys(canciones))
        return canciones
    except FileNotFoundError:
        print(f"❌ Error: no se encontró '{archivo}'.")
        exit(1)

def generar_carton(canciones, dimension, centro_libre):
    total = dimension * dimension
    necesarias = total - 1 if centro_libre else total
    if len(canciones) < necesarias:
        raise ValueError(f"Se necesitan {necesarias} canciones; tienes {len(canciones)}.")
    seleccion = random.sample(canciones, necesarias)
    random.shuffle(seleccion)
    carton = [None] * total
    if centro_libre:
        centro_idx = dimension // 2 * dimension + dimension // 2
        posiciones = [i for i in range(total) if i != centro_idx]
    else:
        posiciones = list(range(total))
    for i, pos in enumerate(posiciones):
        carton[pos] = seleccion[i]
    return carton

def calcular_tamano_fuente(texto, ancho_celda, alto_celda, margen=0.15*cm, min_size=4, max_size=12):
    ancho_util = ancho_celda - 2*margen
    alto_util = alto_celda - 2*margen
    for size in range(max_size, min_size-1, -1):
        max_chars = max(1, int(ancho_util / (size * 0.55)))
        lines = textwrap.wrap(texto, width=max_chars)
        if not lines:
            lines = [texto[i:i+max_chars] for i in range(0, len(texto), max_chars)]
        alto_total = len(lines) * (size * 1.2)
        if alto_total <= alto_util:
            return size
    return min_size

def dibujar_carton(c, x, y, carton, dimension, lado, titulo, numero=None):
    """
    Dibuja un cartón cuadrado de lado 'lado' en la posición (x, y).
    El título se dibuja encima, a una distancia fija de 0.8 cm.
    """
    c.saveState()

    # ---- Título (separado 0.8 cm por encima del borde superior) ----
    c.setFont(FUENTE_TITULO, TAMANO_TITULO)
    c.setFillColorRGB(*COLOR_TITULO)
    c.drawCentredString(x + lado/2, y + lado + 0.8*cm, titulo)

    # ---- Número de cartón (esquina superior derecha) ----
    if numero is not None:
        c.setFont("Helvetica", 10)
        c.setFillColorRGB(0.3, 0.3, 0.3)
        c.drawRightString(x + lado - 0.3*cm, y + lado - 0.3*cm, f"Nº {numero}")

    # ---- Fondo del cartón (redondeado) ----
    c.setFillColorRGB(*COLOR_FONDO_CARTON)
    c.setStrokeColorRGB(*COLOR_BORDE_CARTON)
    c.setLineWidth(3)
    c.roundRect(x, y, lado, lado, RADIO_REDONDEO, fill=1, stroke=1)

    # ---- Celdas ----
    cell_w = (lado - 2*MARGEN_CELDA) / dimension
    cell_h = (lado - 2*MARGEN_CELDA) / dimension
    c.setStrokeColorRGB(*COLOR_BORDE_CELDA)
    c.setLineWidth(1)

    centro_idx = dimension // 2 * dimension + dimension // 2 if CENTRO_LIBRE else -1

    for i in range(dimension):
        for j in range(dimension):
            idx = i * dimension + j
            texto = carton[idx]
            cx = x + MARGEN_CELDA + j * cell_w
            cy = y + MARGEN_CELDA + (dimension - 1 - i) * cell_h

            # Color de fondo alterno
            if (i + j) % 2 == 0:
                c.setFillColorRGB(*COLOR_CELDA_PAR)
            else:
                c.setFillColorRGB(*COLOR_CELDA_IMPAR)

            if CENTRO_LIBRE and idx == centro_idx:
                c.setFillColorRGB(1.0, 0.8, 0.0)
                c.rect(cx, cy, cell_w, cell_h, fill=1, stroke=1)
                c.setFont("Helvetica-Bold", min(cell_w, cell_h) * 0.4)
                c.setFillColorRGB(1, 1, 1)
                c.drawCentredString(cx + cell_w/2, cy + cell_h/2 - 0.1*cm, "★")
                continue

            c.rect(cx, cy, cell_w, cell_h, fill=1, stroke=1)

            # Texto
            tamano = calcular_tamano_fuente(texto, cell_w, cell_h)
            c.setFont(FUENTE, tamano)
            c.setFillColorRGB(*COLOR_TEXTO)

            max_chars = max(1, int((cell_w - 0.3*cm) / (tamano * 0.55)))
            lines = textwrap.wrap(texto, width=max_chars)
            if not lines:
                lines = [texto[i:i+max_chars] for i in range(0, len(texto), max_chars)]
            if len(lines) > 3:
                lines = lines[:3]
                if len(lines[-1]) > 3:
                    lines[-1] = lines[-1][:-3] + "..."

            line_h = tamano * 1.2
            total_h = len(lines) * line_h
            start_y = cy + (cell_h - total_h) / 2 + tamano * 0.4
            for k, line in enumerate(lines):
                y_text = start_y + k * line_h
                c.setFillColorRGB(*COLOR_TEXTO)
                c.drawCentredString(cx + cell_w/2, y_text, line)

    # ---- Borde redondeado final (trazo) ----
    c.setStrokeColorRGB(*COLOR_BORDE_CARTON)
    c.setLineWidth(3)
    c.roundRect(x, y, lado, lado, RADIO_REDONDEO, fill=0, stroke=1)

    c.restoreState()

def generar_pdf(cartones, dimension, archivo_salida):
    c = canvas.Canvas(archivo_salida, pagesize=A4)
    width, height = A4

    # Márgenes y separación mejorada
    margen_lateral = 1.5*cm
    espacio_entre_cartones = 1.2*cm          # Espacio entre la base del título inferior y el borde superior del cartón superior
    altura_titulo_y_margen = 0.8*cm + 0.3*cm # título + un poco más de margen

    # Calcular lado máximo para que quepan dos cartones en vertical
    ancho_disponible = width - 2*margen_lateral
    # Alto disponible: restando márgenes superior e inferior y el espacio extra para títulos
    # Cada cartón ocupa: lado + altura_titulo_y_margen (espacio para el título encima)
    # Queremos dos slots: 2*lado + 2*altura_titulo_y_margen + espacio_entre_cartones
    alto_disponible = height - 2*cm  # margen superior e inferior genérico
    # Ajustamos el lado considerando que el espacio para títulos no debe consumir demasiado
    # Resolvemos: lado = (alto_disponible - 2*altura_titulo_y_margen - espacio_entre_cartones) / 2
    lado_calculado = (alto_disponible - 2*altura_titulo_y_margen - espacio_entre_cartones) / 2
    lado = min(ancho_disponible, lado_calculado)

    # Si el lado es demasiado pequeño, forzamos un mínimo
    if lado < 5*cm:
        lado = 5*cm
        print("Advertencia: el cartón es pequeño, ajusta márgenes o reduce la dimensión.")

    # Posiciones verticales:
    # El bloque total ocupa: 2*lado + 2*altura_titulo_y_margen + espacio_entre_cartones
    bloque_total = 2*lado + 2*altura_titulo_y_margen + espacio_entre_cartones
    y_base = (height - bloque_total) / 2  # base del cartón inferior

    # Cartón inferior: y0 = y_base
    y0 = y_base
    # Cartón superior: y1 = y0 + lado + altura_titulo_y_margen + espacio_entre_cartones
    y1 = y0 + lado + altura_titulo_y_margen + espacio_entre_cartones

    # Centrado horizontal
    x = (width - lado) / 2

    for idx, carton in enumerate(cartones):
        if idx % 2 == 0 and idx > 0:
            c.showPage()
        if idx % 2 == 0:
            dibujar_carton(c, x, y1, carton, dimension, lado, TITULO, numero=idx+1)
        else:
            dibujar_carton(c, x, y0, carton, dimension, lado, TITULO, numero=idx+1)

    c.save()
    print(f"✅ PDF generado: {archivo_salida}")

def main():
    print("🎵 Generador de Bingo Musical")
    print("=" * 50)

    canciones = leer_canciones(ARCHIVO_CANCIONES)
    print(f"📚 {len(canciones)} canciones únicas cargadas.")

    try:
        dim = int(input(f"Dimensión del cartón (ej. 3,4,5...)? [default {DIMENSION}]: ") or DIMENSION)
        if dim < 2:
            dim = 2
    except:
        dim = DIMENSION

    necesarias = dim * dim - (1 if CENTRO_LIBRE else 0)
    if len(canciones) < necesarias:
        print(f"⚠️  Necesitas {necesarias} canciones, tienes {len(canciones)}. Reduce la dimensión.")
        return

    try:
        num = int(input(f"Número de cartones? [default {NUM_CARTONES}]: ") or NUM_CARTONES)
        if num <= 0:
            num = NUM_CARTONES
    except:
        num = NUM_CARTONES

    print(f"🔄 Generando {num} cartones de {dim}x{dim}...")
    cartones = []
    for _ in range(num):
        try:
            cartones.append(generar_carton(canciones, dim, CENTRO_LIBRE))
        except ValueError as e:
            print(f"❌ Error: {e}")
            return

    generar_pdf(cartones, dim, NOMBRE_PDF)
    print(f"🎉 ¡Listo! {len(cartones)} cartones en '{NOMBRE_PDF}'.")
    guardar_json(cartones, archivo="cartones.json")


    # Después de leer las canciones
    with open("canciones.json", "w", encoding="utf-8") as f:
        json.dump(canciones, f, ensure_ascii=False, indent=2)


if __name__ == "__main__":
    main()