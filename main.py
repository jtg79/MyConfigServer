import requests
import re
import base64
import html
from datetime import datetime

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    configs = []
    # الگوی سالم و بدون پرانتز شما
    pattern = r'vless://[^\s<>"]+|vmess://[^\s<>"]+|trojan://[^\s<>"]+|ss://[^\s<>"]+|ssr://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'
    
    # دریافت تاریخ امروز به فرمت تلگرام (مثلاً February 06)
    today = datetime.now().strftime("%B %d")

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            
            if r.status_code == 200:
                # جدا کردن پیام‌ها از هم برای بررسی تاریخ هر کدام
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                
                ch_configs = []
                for msg in messages:
                    # شرط اصلی: فقط اگر تاریخ امروز در متن پیام بود
                    if today in msg:
                        found = re.findall(pattern, html.unescape(msg))
                        ch_configs.extend(found)
                
                # انتخاب حداکثر ۱۰ مورد آخر از کانفیگ‌های امروزِ این کانال
                latest_today = ch_configs[-10:]
                
                for link in latest_today:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    if "#" in clean_link:
                        clean_link = clean_link.split("#")[0]
                    
                    final_link = f"{clean_link}#@{clean_ch}"
                    configs.append(final_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        # اگر هیچ کانفیگی پیدا نشد، فایل را خالی نمی‌کنیم تا اشتراک قبلی نپرد
        print("هیچ کانفیگ جدیدی در ۶ ساعت اخیر یافت نشد.")
        return

    final_text = "\n".join(unique_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
