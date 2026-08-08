#!/usr/bin/env python3
"""
monitor.py — Main monitor script with unified cache and error handling.
"""
import json
import logging
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from config import CHANNELS, PHOTO_CHANNELS, CACHE_FILE, OUTPUT_DIR
from scraper import scrape_channel
from image_gen import generate_price_image
from telegram_post import post_photo

# ── Logging ────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ── Cache Management ───────────────────────────────────────────────────
def load_cache():
    """Load cache from file."""
    if CACHE_FILE.exists():
        try:
            return json.loads(CACHE_FILE.read_text())
        except json.JSONDecodeError:
            logger.warning("Cache file corrupted, starting fresh")
    return {}


def save_cache(cache):
    """Save cache to file."""
    CACHE_FILE.write_text(json.dumps(cache, indent=2, ensure_ascii=False))


def get_last_msg_id(cache, channel):
    """Get last processed message ID for channel."""
    return cache.get(channel, {}).get('last_msg_id')


def set_last_msg_id(cache, channel, msg_id):
    """Set last processed message ID for channel."""
    if channel not in cache:
        cache[channel] = {}
    cache[channel]['last_msg_id'] = msg_id
    cache[channel]['last_check'] = datetime.now().isoformat()


# ── Caption Builder ────────────────────────────────────────────────────
def build_caption(channel, prices, source_url):
    """Build Persian caption for price post."""
    tz = timezone(timedelta(hours=3, minutes=30))
    now = datetime.now(tz)
    
    import jdatetime
    jd = jdatetime.datetime.fromgregorian(datetime=now)
    
    from config import FA_DAYS
    day_name = FA_DAYS.get(jd.strftime('%A'), jd.strftime('%A'))
    shamsi = f'{day_name}، {jd.strftime("%Y/%m/%d")}'
    
    # Channel display name
    channel_names = {
        'saebsteelco': 'فولاد صائب تبریز',
        'zafarSteelbonab': 'فولاد ظفر بناب',
        'FSDTABRIZ': 'فولاد سازان دقيقی هشترود',
        'sfk_steels': 'SFK Steels',
        'dorpadtabriz_co': 'گروه صنعتی درپاد',
        'afasteel': 'آذر فولاد امین',
        'oxintrading': 'اوکسین تریدینگ',
        'steelradhamedan': 'فولاد راد همدان',
        'damirbazar': 'دمیر بازار',
        'pardissteel1': 'پردیس استیل',
        'ArianSteel': 'آرین استیل',
        'javidsteel_bonab': 'جاوید استیل بناب',
        'Fuladnab': 'فولاد ناب',
    }
    
    display_name = channel_names.get(channel, channel)
    
    caption = f"""<b>📊 قیمت روز {display_name}</b>
🗓 {shamsi}
✅ ثبت سفارش با تایید قیمت

✅ شرکت فولاد آروین تجارت امین ایرانیان ✅
(لوله ,پروفیل ,نبشی ,ناودانی ,مفتول ,ورق شیت ,تسمه ,میلگرد آجدار ,سه پرآهنی ,ستونی ,تیرآهن)

شعبه تبریز
☎️ 04134461257
☎️ 04134479961-4
-------------------------------------------
شعبه مرکزی تهران 
☎️ 021-48814676
☎️ 021-48814677

🔗 <a href="{source_url}">منبع: @{channel}</a>"""
    
    return caption


# ── Monitor Single Channel ─────────────────────────────────────────────
def monitor_channel(channel, cache):
    """
    Monitor a single channel and post if new prices found.
    
    Returns:
        str: Status message
    """
    logger.info(f"Checking @{channel}...")
    
    # Scrape channel
    result = scrape_channel(channel)
    
    if result is None:
        return f"@{channel}: ❌ No data"
    
    # Check for new message
    msg_id = result['link'].split('/')[-1] if result['link'] else None
    last_id = get_last_msg_id(cache, channel)
    
    if msg_id and msg_id == last_id:
        return f"@{channel}: ⚪ No new posts"
    
    # Update cache
    if msg_id:
        set_last_msg_id(cache, channel, msg_id)
    
    # Check if has prices
    if not result['prices']:
        if result['is_photo'] and result['photo_url']:
            return f"@{channel}: 📸 Photo-only (needs vision)"
        return f"@{channel}: ⚠️ No parseable prices"
    
    # Generate image
    try:
        OUTPUT_DIR.mkdir(exist_ok=True)
        img_path = str(OUTPUT_DIR / f'price_{channel}.png')
        generate_price_image(channel, result['prices'], result['link'], img_path)
    except Exception as e:
        logger.error(f"Image generation failed for @{channel}: {e}")
        return f"@{channel}: ❌ Image generation failed"
    
    # Build caption
    caption = build_caption(channel, result['prices'], result['link'])
    
    # Post to channel
    try:
        post_result = post_photo(img_path, caption, result['link'])
        if post_result.get('ok'):
            msg_id = post_result['result']['message_id']
            return f"@{channel}: ✅ Posted (msg #{msg_id})"
        else:
            return f"@{channel}: ❌ Post failed"
    except Exception as e:
        logger.error(f"Post failed for @{channel}: {e}")
        return f"@{channel}: ❌ Post failed"


# ── Main ───────────────────────────────────────────────────────────────
def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Steel Price Monitor')
    parser.add_argument('channel', nargs='?', help='Specific channel to monitor')
    parser.add_argument('--all', action='store_true', help='Monitor all channels')
    parser.add_argument('--list', action='store_true', help='List all channels')
    args = parser.parse_args()
    
    if args.list:
        print("Monitored channels:")
        for ch in CHANNELS:
            ch_type = "📸 Photo" if ch in PHOTO_CHANNELS else "📝 Text"
            print(f"  - @{ch} ({ch_type})")
        return
    
    cache = load_cache()
    
    channels_to_check = [args.channel] if args.channel else CHANNELS
    
    results = []
    for channel in channels_to_check:
        if channel not in CHANNELS:
            results.append(f"@{channel}: ❌ Unknown channel")
            continue
        
        result = monitor_channel(channel, cache)
        results.append(result)
        
        # Save cache after each channel
        save_cache(cache)
    
    # Print summary
    print("\n" + "="*50)
    print("Steel Price Monitor — Summary")
    print("="*50)
    for r in results:
        print(r)
    print("="*50)


if __name__ == '__main__':
    main()
