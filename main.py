import requests
import re
import base64
import html
import socket
from datetime import datetime

# تابع تستر داخلی برای بررسی زنده بودن پورت سرور
def is_port_open(link):
    try:
        if '@' in link:
            # استخراج تمیز آدرس و پورت برای تست
            server_part = link.split('@')[1].split('/')[0].split('?')[0].split('#')[0]
            if ':' in server_part:
                address, port = server_part.split(':')
                port = int(port)
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    return s.connect_ex((address, port)) == 0
        return False 
    except:
        return False

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except: return

    all_data = [] 
    # الگوی تخت و اصلاح‌شده برای استخراج کامل لینک
    pattern = r'vless://[^\s<>"]+|trojan://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            # هدر مرورگر برای جلوگیری از بلاک شدن توسط تلگرام
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            
            if r.status_code == 200:
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                for msg in messages:
                    # استخراج زمان دقیق انتشار پیام
                    time_match = re.search(r'<time [^>]*datetime="([^"]+)"', msg)
                    if time_match:
                        timestamp = time_match.group(1)
                        links = re.findall(pattern, html.unescape(msg))
                        for link in links:
                            clean_link = link.strip().split('<')[0].split('"')[0]
                            all_data.append({
                                'main': clean_link.split('#')[0],
                                'time': timestamp,
                                'channel': clean_ch
                            })
        except: continue

    # مرتب‌سازی بر اساس زمان (از قدیمی به جدید)
    all_data.sort(key=lambda x: x['time'])

    final_configs = []
    seen_contents = {} # ذخیره محتوا و تعداد تکرار آن

    # گام اول: شمارش تکرارها برای شناسایی کانفیگ‌های کپی شده
    content_counts = {}
    for item in all_data:
        content_counts[item['main']] = content_counts.get(item['main'], 0) + 1

    # گام دوم: انتخاب و برچسب‌گذاری
    processed_contents = set()
    for item in all_data:
        config_content = item['main']
        
        if config_content not in processed_contents:
            # فیلتر امنیتی Vless
            if "vless" in config_content and "security=tls" not in config_content and "security=reality" not in config_content:
                continue
            
            # تست زنده بودن سرور
            if is_port_open(config_content):
                processed_contents.add(config_content)
                
                # اگر این کانفیگ در بیش از یک کانال بوده، به قدیمی‌ترین نسخه Verified اضافه کن
                if content_counts[config_content] > 1:
                    tag = f"@{item['channel']}_Verified"
                else:
                    tag = f"@{item['channel']}"
                
                final_configs.append(f"{config_content}#{tag}")

    if not final_configs: return

    final_text = "\n".join(final_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
