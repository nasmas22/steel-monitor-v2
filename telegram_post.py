#!/usr/bin/env python3
"""
telegram_post.py — Telegram Bot API integration with retry logic.
"""
import logging
import requests
from config import get_bot_token, TARGET_CHANNEL

logger = logging.getLogger(__name__)

MAX_RETRIES = 3
RETRY_DELAY = 2


def post_photo(img_path, caption, source_url=None):
    """
    Post photo with caption to Telegram channel.
    
    Args:
        img_path: Path to image file
        caption: Caption text (HTML supported)
        source_url: Optional source URL to append
    
    Returns:
        dict: Telegram API response
    """
    token = get_bot_token()
    url = f'https://api.telegram.org/bot{token}/sendPhoto'
    
    # Add source link if provided
    if source_url:
        caption += f'\n\n🔗 <a href="{source_url}">منبع</a>'
    
    for attempt in range(MAX_RETRIES):
        try:
            with open(img_path, 'rb') as f:
                response = requests.post(
                    url,
                    data={
                        'chat_id': TARGET_CHANNEL,
                        'caption': caption,
                        'parse_mode': 'HTML',
                    },
                    files={'photo': f},
                    timeout=30,
                )
            
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Posted successfully: msg_id={result['result']['message_id']}")
                return result
            else:
                error = result.get('description', 'Unknown error')
                logger.error(f"Telegram API error: {error}")
                
                # Don't retry on client errors (4xx)
                if response.status_code < 500:
                    return result
                
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    return {'ok': False, 'description': 'All retries failed'}


def post_text(text, parse_mode='HTML'):
    """
    Post text message to Telegram channel.
    
    Args:
        text: Message text
        parse_mode: Parse mode (HTML or Markdown)
    
    Returns:
        dict: Telegram API response
    """
    token = get_bot_token()
    url = f'https://api.telegram.org/bot{token}/sendMessage'
    
    for attempt in range(MAX_RETRIES):
        try:
            response = requests.post(
                url,
                json={
                    'chat_id': TARGET_CHANNEL,
                    'text': text,
                    'parse_mode': parse_mode,
                },
                timeout=30,
            )
            
            result = response.json()
            
            if result.get('ok'):
                logger.info(f"Posted text: msg_id={result['result']['message_id']}")
                return result
            else:
                error = result.get('description', 'Unknown error')
                logger.error(f"Telegram API error: {error}")
                return result
                
        except requests.RequestException as e:
            logger.warning(f"Attempt {attempt + 1} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                import time
                time.sleep(RETRY_DELAY * (attempt + 1))
    
    return {'ok': False, 'description': 'All retries failed'}
