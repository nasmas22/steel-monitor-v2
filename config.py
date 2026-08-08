#!/usr/bin/env python3
"""
config.py — Central configuration with env fallback.
"""
import os
from pathlib import Path

# ── Paths ──────────────────────────────────────────────────────────────
HERMES_HOME = Path(os.environ.get('HERMES_HOME', os.path.expanduser('~/.hermes')))
ENV_FILE = HERMES_HOME / '.env'
CACHE_FILE = Path(__file__).parent / '.price_cache.json'
FONTS_DIR = Path(__file__).parent / 'fonts'
OUTPUT_DIR = Path(__file__).parent / 'output'

# ── Telegram ───────────────────────────────────────────────────────────
TARGET_CHANNEL = '-1004431236647'  # @IronwarePriceTestChannel

def get_bot_token():
    """Get bot token from env file, fallback to env variable."""
    # Try env file first
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text().splitlines():
            if line.startswith('TELEGRAM_BOT_TOKEN='):
                return line.split('=', 1)[1].strip()
    
    # Fallback to env variable
    token = os.environ.get('TELEGRAM_BOT_TOKEN')
    if token:
        return token
    
    raise ValueError("TELEGRAM_BOT_TOKEN not found in .env or environment")

# ── Channels ───────────────────────────────────────────────────────────
CHANNELS = [
    # Text-based channels
    'saebsteelco',
    'zafarSteelbonab',
    'FSDTABRIZ',
    'sfk_steels',
    'dorpadtabriz_co',
    'afasteel',
    'oxintrading',
    'steelradhamedan',
    # Photo-only channels (need vision)
    'damirbazar',
    'pardissteel1',
    'ArianSteel',
    'javidsteel_bonab',
    # Other
    'Fuladnab',
]

PHOTO_CHANNELS = {'damirbazar', 'pardissteel1', 'ArianSteel', 'javidsteel_bonab'}

# ── Company Info ───────────────────────────────────────────────────────
COMPANY_NAME = 'شرکت فولاد آروین تجارت امین ایرانیان'
COMPANY_PRODUCTS = 'لوله, پروفیل, نبشی, ناودانی, مفتول, ورق شیت, تسمه, میلگرد آجدار, سه پرآهنی, ستونی, تیرآهن'
CONTACTS = {
    'tabriz': ['041-34461257', '041-34479961-4'],
    'tehran': ['021-48814676', '021-48814677'],
}

# ── Persian Helpers ────────────────────────────────────────────────────
FA_NUMS = {'۰':'0','۱':'1','۲':'2','۳':'3','۴':'4','۵':'5','۶':'6','۷':'7','۸':'8','۹':'9'}
FA_DAYS = {
    'Saturday':'شنبه','Sunday':'یکشنبه','Monday':'دوشنبه',
    'Tuesday':'سه‌شنبه','Wednesday':'چهارشنبه','Thursday':'پنجشنبه','Friday':'جمعه'
}

def fa_to_en(s):
    """Convert Persian numerals to English."""
    for k, v in FA_NUMS.items():
        s = s.replace(k, v)
    return s
