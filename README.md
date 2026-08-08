# 🇮🇷 مانیتور قیمت فولاد ایران (v2)

مانیتور خودکار قیمت میلگرد و فولاد از ۱۳ کانال تلگرام ایرانی، با میانگین‌گیری هوشمند، تولید عکس برنددار و انتشار خودکار.

## ✨ امکانات

- **مانیتور لحظه‌ای** — هر ۱۰ دقیقه کانال‌ها رو چک میکنه
- **استخراج هوشمند قیمت** — با پشتیبانی از اعداد فارسی و عربی
- **یکپارچه‌سازی Vision AI** — خواندن قیمت از عکس با هوش مصنوعی
- **تولید عکس برنددار** — کارت قیمت حرفه‌ای با برند شرکت
- **انتشار خودکار** — پست در کانال تلگرام با لینک منبع
- **جلوگیری از تکرار** — ردیابی آخرین پست پردازش شده هر کانال
- **تشخیص داده پرت** — حذف قیمت‌های بیش از ۲۰٪ از میانه
- **Retry Logic** — تلاش مجدد در صورت خطا
- **Error Handling** — مدیریت صحیح خطاها

## 📁 ساختار پروژه

```
steel-monitor-v2/
├── config.py           # تنظیمات مرکزی
├── scraper.py          # اسکرپر تلگرام
├── image_gen.py        # تولید عکس
├── telegram_post.py    # ارسال به تلگرام
├── monitor.py          # اسکریپت اصلی
├── fonts/              # فونت‌ها
│   ├── Vazirmatn-Bold.ttf
│   └── Vazirmatn.ttf
├── output/             # عکس‌های تولید شده
├── .price_cache.json   # کش پیام‌ها
└── README.md
```

## 🚀 نحوه استفاده

```bash
# نصب پیش‌نیازها
pip install requests beautifulsoup4 Pillow jdatetime arabic-reshaper python-bidi

# چک کردن یک کانال خاص
python3 monitor.py saebsteelco

# چک کردن تمام کانال‌ها
python3 monitor.py --all

# نمایش لیست کانال‌ها
python3 monitor.py --list
```

## 🔌 کانال‌های تحت نظر (۱۳)

### کانال‌های متنی (۹)
| کانال | توضیحات |
|-------|---------|
| @saebsteelco | فولاد صائب تبریز |
| @zafarSteelbonab | مجتمع فولاد ظفر بناب |
| @FSDTABRIZ | فولاد سازان دقيقی هشترود |
| @sfk_steels | SFK Steels |
| @dorpadtabriz_co | گروه صنعتی درپاد |
| @afasteel | آذر فولاد امین |
| @oxintrading | اوکسین تریدینگ |
| @steelradhamedan | فولاد راد همدان |
| @Fuladnab | فولاد ناب |

### کانال‌های فقط عکس (۴) — نیاز به Vision
| کانال | توضیحات |
|-------|---------|
| @damirbazar | دمیر بازار |
| @pardissteel1 | پردیس استیل |
| @ArianSteel | آرین استیل |
| @javidsteel_bonab | جاوید استیل بناب |

## ⚙️ تنظیمات

### متغیرهای محیطی
```bash
# در ~/.hermes/.env یا متغیر محیطی
TELEGRAM_BOT_TOKEN=your_bot_token
```

### تنظیمات کرن‌جاب (Hermes Agent)
- **زمانبندی:** `*/10 8-16 * * 6,0-4`
- **روزها:** شنبه تا پنجشنبه
- **ساعات:** ۸ صبح تا ۵ عصر
- **منطقه زمانی:** Asia/Tehran

## 🛠 پیش‌نیازها

```bash
pip install requests beautifulsoup4 Pillow jdatetime arabic-reshaper python-bidi
```

## 📜 لایسنس

MIT
