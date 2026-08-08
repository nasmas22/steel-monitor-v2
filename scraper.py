#!/usr/bin/env python3
"""
scraper.py — Telegram channel scraper with retry logic.
"""
import re
import time
import logging
import requests
from bs4 import BeautifulSoup
from config import fa_to_en, PHOTO_CHANNELS

logger = logging.getLogger(__name__)

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
TIMEOUT = 15
MAX_RETRIES = 3
RETRY_DELAY = 2

# ── Price Regex Patterns ───────────────────────────────────────────────

def parse_price(val):
    """Parse price string to integer (in toman)."""
    if not val:
        return None
    
    # Clean and convert Persian digits
    val = fa_to_en(val.strip())
    val = val.replace(',', '').replace('.', '').replace(' ', '')
    
    # Remove non-numeric chars
    val = re.sub(r'[^\d]', '', val)
    
    if not val:
        return None
    
    try:
        price = int(val)
    except ValueError:
        return None
    
    # Auto-detect unit: if > 100000, assume rial and convert to toman
    # Reasonable toman range: 5,000 - 200,000
    if price > 100_000:
        price = price // 10
    
    # Sanity check
    if price < 5_000 or price > 500_000:
        return None
    
    return price


def extract_prices_from_text(text):
    """Extract prices from message text using multiple patterns."""
    prices = []
    
    if not text:
        return prices
    
    # Pattern 1: میلگرد آجدار A2 سایز 8: 760000
    for m in re.finditer(
        r'(میلگرد|ميلگرد|تیرآهن|ti*rahan|ورق|sheet)'
        r'\s*(?:آجدار\s*)?(A[234]|B500B|A500C)?'
        r'\s*(?:سایز|سايز|SA)?\s*(\d+)?'
        r'(?:\s*(?:الی|تا)\s*(\d+))?'
        r'\s*(?:←|:|\|)\s*\|?\s*([\d,\.]+)',
        text, re.IGNORECASE
    ):
        prod = m.group(1)
        grade = m.group(2) or ''
        size_base = m.group(3) or ''
        size_range = m.group(4) or ''
        price = parse_price(m.group(5))
        
        # Build size string
        if size_base and size_range:
            size = f'{size_base} الی {size_range}'
        elif size_base:
            size = size_base
        else:
            size = ''
        
        if price:
            name = f'{prod}'
            if grade:
                name += f' {grade}'
            if size:
                name += f' {size}'
            prices.append({'product': name.strip(), 'price': price})
    
    # Pattern 2: سایز 8 | گرید (A2) ← 750,000
    for m in re.finditer(
        r'سایز\s*(\d+)\s*\|\s*گرید\s*\((A[234]|B500B|A500C)\)\s*←\s*([\d,\.]+)',
        text
    ):
        size, grade, price_raw = m.group(1), m.group(2), m.group(3)
        price = parse_price(price_raw)
        if price:
            prices.append({'product': f'میلگرد {grade} {size}', 'price': price})
    
    # Pattern 3: sfk_steels format: 72.300
    for m in re.finditer(
        r'(میلگرد|تیرآهن)\s*(A[234])?\s*(\d+)?\s*[:|]\s*([\d\.]+)',
        text
    ):
        prod = m.group(1) or 'میلگرد'
        grade = m.group(2) or ''
        size = m.group(3) or ''
        price = parse_price(m.group(4))
        if price:
            name = f'{prod} {grade} {size}'.strip()
            prices.append({'product': name, 'price': price})
    
    return prices


def scrape_channel(channel, retries=MAX_RETRIES):
    """
    Scrape a Telegram channel for latest price post.
    
    Returns:
        dict: {'text': str, 'prices': list, 'link': str, 'is_photo': bool, 'photo_url': str}
        None: if no prices found
    """
    url = f'https://t.me/s/{channel}'
    
    for attempt in range(retries):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
            resp.raise_for_status()
            
            soup = BeautifulSoup(resp.text, 'html.parser')
            messages = soup.find_all('div', class_='tgme_widget_message_wrap')
            
            if not messages:
                logger.warning(f"@{channel}: No messages found")
                return None
            
            # Check latest message
            last_msg = messages[-1]
            text_el = last_msg.find('div', class_='tgme_widget_message_text')
            photo_el = last_msg.find('a', class_='tgme_widget_message_photo_wrap')
            date_el = last_msg.find('time')
            
            text = text_el.get_text(separator='\n', strip=True) if text_el else ''
            has_photo = bool(photo_el)
            msg_date = date_el['datetime'][:10] if date_el else ''
            
            # Build message link
            msg_id = last_msg.get('data-post', '').split('/')[-1] if last_msg.get('data-post') else ''
            link = f'https://t.me/{channel}/{msg_id}' if msg_id else url
            
            # Extract photo URL if exists
            photo_url = None
            if photo_el:
                style = photo_el.get('style', '')
                url_match = re.search(r"url\('(.+?)'\)", style)
                if url_match:
                    photo_url = url_match.group(1)
            
            # Try to extract prices from text
            prices = extract_prices_from_text(text)
            
            if prices:
                logger.info(f"@{channel}: Found {len(prices)} prices from text")
                return {
                    'text': text,
                    'prices': prices,
                    'link': link,
                    'is_photo': False,
                    'photo_url': None,
                    'msg_date': msg_date,
                }
            
            # If photo-only channel, return photo info
            if channel in PHOTO_CHANNELS and has_photo and photo_url:
                logger.info(f"@{channel}: Photo-only channel, needs vision")
                return {
                    'text': text,
                    'prices': [],
                    'link': link,
                    'is_photo': True,
                    'photo_url': photo_url,
                    'msg_date': msg_date,
                }
            
            # Text but no parseable prices
            if text:
                logger.info(f"@{channel}: Post found but no parseable prices")
                return {
                    'text': text,
                    'prices': [],
                    'link': link,
                    'is_photo': False,
                    'photo_url': None,
                    'msg_date': msg_date,
                }
            
            return None
            
        except requests.RequestException as e:
            logger.warning(f"@{channel}: Attempt {attempt+1} failed: {e}")
            if attempt < retries - 1:
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    logger.error(f"@{channel}: All {retries} attempts failed")
    return None
