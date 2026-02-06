import requests
import re
import base64
import html
import time
from datetime import datetime

def get_config_identity(link):
    """استخراج شناسه هوشمند برای تشخیص تکراری‌ها"""
    try:
        if link.startswith('vless://'):
            match = re.search(r'vless://([^@]+)@', link)
            if match: return f"VLESS_ID:{match.group(1)}"
        
        if '@' in link:
            server_part = link.split('@')[1].split('/')[0].split('?')[0].split('#')[0]
            return f"SERVER_ID:{server_part}"
    except: return None
    return None

def collect():
    # خواندن ۷ کانال اصلی از فایل
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except: return

    all_raw_data = [] 
    # پترن دقیق برای استخراج پروتکل‌های باکیفیت
    pattern = r'vless://[^\s<>"]+|trojan://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            # فقط صفحه اول هر کانال را می‌خوانیم (برای سرعت و تازگی ۵ تای آخر)
            r = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            if r.status_code == 200:
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                
                channel_configs = []
                # بررسی پیام‌ها از جدید به قدیم
                for msg in reversed(messages):
                    time_match = re.search(r'datetime="([^"]+)"', msg)
                    if time_match:
                        timestamp = time_match.group(1)
                        links = re.findall(pattern, html.unescape(msg))
                        for link in links:
                            full_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                            config_id = get_config_identity(full_link)
                            if config_id:
                                channel_configs.append({
                                    'id': config_id,
                                    'full': full_link,
                                    'time': timestamp,
                                    'channel': clean_ch
                                })
                    
                    # به محض اینکه ۵ کانفیگ برای این کانال پیدا شد، برو سراغ کانال بعدی
                    if len(channel_configs) >= 5:
                        break
                
                all_raw_data.extend(channel_configs)
        except: continue

    # ۱. مرتب‌سازی بر اساس زمان (قدیمی به جدید) برای حفظ حق انتشار
    all_raw_data.sort(key=lambda x: x['time'])

    # ۲. شناسایی اولین منتشرکننده و شمارش تکرار
    first_publishers = {} 
    occurrence_count = {}
    for item in all_raw_data:
        c_id = item['id']
        occurrence_count[c_id] = occurrence_count.get(c_id, 0) + 1
        if c_id not in first_publishers:
            first_publishers[c_id] = item['channel']

    final_configs = []
    processed_ids = set()

    # ۳. فیلتر نهایی و ساخت لیست خروجی
    for item in all_raw_data:
        c_id = item['id']
        if c_id not in processed_ids and item['channel'] == first_publishers[c_id]:
            
            full_link = item['full']
            # فیلتر امنیتی Vless: فقط TLS یا Reality
            if "vless" in full_link and not any(s in full_link for s in ["security=tls", "security=reality"]):
                continue
            
            processed_ids.add(c_id)
            count = occurrence_count[c_id]
            
            # برچسب‌گذاری بر اساس منبع و تعداد تکرار
            if count > 1:
                tag = f"@{item['channel']}_Verified({count})"
            else:
                tag = f"@{item['channel']}"
            
            base_link = full_link.split('#')[0]
            final_configs.append(f"{base_link}#{tag}")

    if not final_configs: return
    
    # تبدیل کل لیست به Base64
    final_text = "\n".join(final_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
