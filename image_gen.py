#!/usr/bin/env python3
"""
image_gen.py — Generate branded price images with RTL Persian support.
"""
import os
from datetime import datetime, timedelta, timezone
import jdatetime
from PIL import Image, ImageDraw, ImageFont
import arabic_reshaper
from bidi.algorithm import get_display

from config import (
    FONTS_DIR, OUTPUT_DIR, COMPANY_NAME, COMPANY_PRODUCTS, CONTACTS, FA_DAYS
)

# ── Load Fonts ─────────────────────────────────────────────────────────
def load_fonts():
    """Load fonts with fallback."""
    try:
        font_bold = ImageFont.truetype(str(FONTS_DIR / 'Vazirmatn-Bold.ttf'), 28)
        font_med = ImageFont.truetype(str(FONTS_DIR / 'Vazirmatn-Bold.ttf'), 22)
        font_small = ImageFont.truetype(str(FONTS_DIR / 'Vazirmatn.ttf'), 18)
        font_tiny = ImageFont.truetype(str(FONTS_DIR / 'Vazirmatn.ttf'), 14)
    except Exception:
        # Fallback to default font
        font_bold = ImageFont.load_default()
        font_med = font_bold
        font_small = font_bold
        font_tiny = font_bold
    
    return font_bold, font_med, font_small, font_tiny

# ── Persian Text Helpers ───────────────────────────────────────────────
def fa(text):
    """Convert Persian text for PIL rendering."""
    reshaped = arabic_reshaper.reshape(text)
    return get_display(reshaped)

def draw_centered(draw, y, text, font, fill, width):
    """Draw centered text."""
    bbox = draw.textbbox((0, 0), fa(text), font=font)
    tw = bbox[2] - bbox[0]
    draw.text(((width - tw) // 2, y), fa(text), font=font, fill=fill)

# ── Get Shamsi Date ────────────────────────────────────────────────────
def get_shamsi_date():
    """Get current date in Shamsi calendar."""
    tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(tz)
    jd = jdatetime.datetime.fromgregorian(datetime=now)
    day_name = FA_DAYS.get(jd.strftime('%A'), jd.strftime('%A'))
    return f'{day_name}، {jd.strftime("%Y/%m/%d")}'

# ── Generate Image ─────────────────────────────────────────────────────
def generate_price_image(channel, prices, source_url, output_path=None):
    """
    Generate branded price image.
    
    Args:
        channel: Channel name
        prices: List of {'product': str, 'price': int}
        source_url: Source URL
        output_path: Optional output path
    
    Returns:
        str: Path to generated image
    """
    font_bold, font_med, font_small, font_tiny = load_fonts()
    
    W = 800
    rows = len(prices)
    H = 420 + rows * 42 + 80
    
    # Create image
    img = Image.new('RGB', (W, H), '#FAFAFA')
    draw = ImageDraw.Draw(img)
    
    # ── Header ─────────────────────────────────────────────────────────
    draw.rounded_rectangle([20, 15, W-20, 75], radius=12, fill='#1A237E')
    draw_centered(draw, 28, COMPANY_NAME, font_bold, '#FFFFFF', W)
    
    # ── Date ───────────────────────────────────────────────────────────
    shamsi = get_shamsi_date()
    draw_centered(draw, 88, shamsi, font_med, '#555555', W)
    
    # ── Table Header ───────────────────────────────────────────────────
    y = 130
    draw.rounded_rectangle([30, y, W-30, y+38], radius=8, fill='#E8EAF6')
    
    cols = [
        ('محصول', 30, 180),
        ('گرید', 180, 330),
        ('سایز', 330, 500),
        ('قیمت (تومان)', 500, W-30)
    ]
    
    for label, x1, x2 in cols:
        bbox = draw.textbbox((0, 0), fa(label), font=font_small)
        tw = bbox[2] - bbox[0]
        draw.text(((x1 + x2 - tw) // 2, y + 8), fa(label), font=font_small, fill='#1A237E')
    
    # ── Table Rows ─────────────────────────────────────────────────────
    y = y + 42
    for i, p in enumerate(prices):
        bg = '#FFFFFF' if i % 2 == 0 else '#F5F5F5'
        draw.rounded_rectangle([30, y, W-30, y+38], radius=6, fill=bg)
        
        # Parse product name for grade/size
        product = p.get('product', '')
        grade = ''
        size = ''
        
        # Try to extract grade and size from product name
        if 'A2' in product:
            grade = 'A2'
        elif 'A3' in product:
            grade = 'A3'
        elif 'B500B' in product:
            grade = 'B500B'
        
        # Extract size (number or range)
        import re
        size_match = re.search(r'(\d+(?:\s*الی\s*\d+)?)', product)
        if size_match:
            size = size_match.group(1)
        
        # Determine product type
        product_type = 'میلگرد'
        if any(x in product.lower() for x in ['تیرآهن', 'ti*rahan']):
            product_type = 'تیرآهن'
        elif any(x in product.lower() for x in ['ورق', 'sheet']):
            product_type = 'ورق'
        
        vals = [
            (product_type, 30, 180),
            (grade, 180, 330),
            (size, 330, 500),
            (f"{p['price']:,}", 500, W-30)
        ]
        
        for val, x1, x2 in vals:
            bbox = draw.textbbox((0, 0), fa(val), font=font_small)
            tw = bbox[2] - bbox[0]
            draw.text(((x1 + x2 - tw) // 2, y + 8), fa(val), font=font_small, fill='#333333')
        
        y += 42
    
    # ── Divider ────────────────────────────────────────────────────────
    y += 5
    draw.line([(40, y), (W-40, y)], fill='#E0E0E0', width=2)
    y += 10
    
    # ── Contact Info ───────────────────────────────────────────────────
    draw_centered(draw, y, f"شعبه تبریز ☎️ {' | '.join(CONTACTS['tabriz'])}", font_small, '#666666', W)
    y += 25
    draw_centered(draw, y, f"شعبه مرکزی تهران ☎️ {' | '.join(CONTACTS['tehran'])}", font_small, '#666666', W)
    
    # ── Save ───────────────────────────────────────────────────────────
    if output_path is None:
        OUTPUT_DIR.mkdir(exist_ok=True)
        output_path = str(OUTPUT_DIR / f'price_{channel}.png')
    
    img.save(output_path, quality=95)
    return output_path
