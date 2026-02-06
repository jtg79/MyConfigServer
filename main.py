import requests
import re
import base64
import html
import socket
from datetime import datetime

def is_port_open(link):
    try:
        if '@' in link:
            server_part = link.split('@')[1].split('/')[0].split('?')[0].split('#')[0]
            if ':' in server_part:
                address, port = server_part.split(':')
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.0)
                    return s.connect_ex((address, int(port))) == 0
        return False 
    except:
        return False

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except: return

    all_raw_data = [] 
    # اصلاح پترن: بدون پرانتز برای استخراج کامل و دقیق لینک
    pattern = r'vless://[^\s<>"]+|trojan://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            r = requests.get(f"https://t.me/s/{clean_ch}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            if r.status_code == 200:
                # جدا کردن پیام‌ها برای استخراج زمان هر کدام
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                for msg in messages:
                    time_match = re.search(r'datetime="([^"]+)"', msg)
                    if time_match:
                        timestamp = time_match.group(1)
                        # استخراج لینک‌ها از محتوای دکود شده پیام
                        decoded_msg = html.unescape(msg)
                        links = re.findall(pattern, decoded_msg)
                        
                        # بررسی ۲۰ لینک آخر هر کانال
                        for link in links[-20:]:
                            clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                            main_content = clean_link.split('#')[0]
                            
                            all_raw_data.append({
                                'main': main_content,
                                'time': timestamp,
                                'channel': clean_ch
                            })
        except: continue

    # ۱. مرتب‌سازی بر اساس زمان (از قدیمی به جدید)
    all_raw_data.sort(key=lambda x: x['time'])

    # ۲. پیدا کردن اولین منتشرکننده و آمار تکرار
    first_publishers = {} 
    content_occurrence_count = {}

    for item in all_raw_data:
        content = item['main']
        content_occurrence_count[content] = content_occurrence_count.get(content, 0) + 1
        if content not in first_publishers:
            first_publishers[content] = item['channel']

    final_configs = []
    processed_for_output = set()

    # ۳. فیلتر نهایی: فقط اولین نسخه از هر محتوا
    for item in all_raw_data:
        content = item['main']
        
        # شرط: فقط اگر این کانال اولین منتشرکننده باشد و قبلاً این محتوا را خروجی نداده باشیم
        if content not in processed_for_output and item['channel'] == first_publishers[content]:
            
            # فیلتر امنیتی Vless
            if "vless" in content and "security=tls" not in content and "security=reality" not in content:
                continue
            
            # تست پورت
            if is_port_open(content):
                processed_for_output.add(content)
                
                # درج Verified فقط برای منبع اصلی در صورت وجود کپی
                is_copied = content_occurrence_count[content] > 1
                tag = f"@{item['channel']}_Verified" if is_copied else f"@{item['channel']}"
                
                final_configs.append(f"{content}#{tag}")

    if not final_configs: return

    final_text = "\n".join(final_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
