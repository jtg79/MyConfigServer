import requests
import re
import base64
import html
import time
from datetime import datetime

# تنظیم تاریخ هدف (۲ فوریه ۲۰۲۶)
TARGET_DATE = datetime(2026, 2, 2)

def get_config_identity(link):
    """استخراج شناسه هوشمند: UUID برای VLESS، و آدرس برای بقیه"""
    try:
        if link.startswith('vless://'):
            match = re.search(r'vless://([^@]+)@', link)
            if match: return f"VLESS_ID:{match.group(1)}"
        
        if '@' in link:
            # استخراج بخش آدرس:پورت
            server_part = link.split('@')[1].split('/')[0].split('?')[0].split('#')[0]
            return f"SERVER_ID:{server_part}"
    except: return None
    return None

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except: return

    all_raw_data = [] 
    pattern = r'vless://[^\s<>"]+|trojan://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            base_url = f"https://t.me/s/{clean_ch}"
            next_before = None
            stop_channel = False
            
            # حلقه ورق زدن تاریخچه تا رسیدن به ۲ فوریه
            while not stop_channel:
                url = f"{base_url}?before={next_before}" if next_before else base_url
                r = requests.get(url, headers=headers, timeout=15)
                if r.status_code != 200: break
                
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                if len(messages) <= 1: break
                
                # پیدا کردن آیدی پیام برای رفتن به صفحه قبل
                id_match = re.search(r'data-post="[^/]*/(\d+)"', messages[1])
                if id_match: next_before = id_match.group(1)

                for msg in messages:
                    time_match = re.search(r'datetime="([^"]+)"', msg)
                    if time_match:
                        msg_time_str = time_match.group(1).split('+')[0]
                        msg_time = datetime.fromisoformat(msg_time_str)
                        
                        # اگر پیام قدیمی‌تر از ۲ فوریه است، این کانال تمام است
                        if msg_time < TARGET_DATE:
                            stop_channel = True
                            continue

                        links = re.findall(pattern, html.unescape(msg))
                        for link in links:
                            full_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                            config_id = get_config_identity(full_link)
                            if config_id:
                                all_raw_data.append({
                                    'id': config_id,
                                    'full': full_link,
                                    'time': msg_time_str,
                                    'channel': clean_ch
                                })
                
                if not next_before: break
                time.sleep(0.1) # وقفه بسیار کوتاه چون تست پورت نداریم
                
        except: continue

    # ۱. مرتب‌سازی زمانی (قدیمی‌ترین اول)
    all_raw_data.sort(key=lambda x: x['time'])

    # ۲. پیدا کردن صاحب اصلی و شمارش کپی‌ها
    first_publishers = {} 
    occurrence_count = {}
    for item in all_raw_data:
        c_id = item['id']
        occurrence_count[c_id] = occurrence_count.get(c_id, 0) + 1
        if c_id not in first_publishers:
            first_publishers[c_id] = item['channel']

    final_configs = []
    processed_ids = set()

    # ۳. فیلتر نهایی بر اساس مالکیت زمانی
    for item in all_raw_data:
        c_id = item['id']
        if c_id not in processed_ids and item['channel'] == first_publishers[c_id]:
            
            full_link = item['full']
            # فیلتر امنیتی Vless (فقط TLS/Reality)
            if "vless" in full_link and not any(s in full_link for s in ["security=tls", "security=reality"]):
                continue
            
            processed_ids.add(c_id)
            count = occurrence_count[c_id]
            
            # برچسب‌گذاری بر اساس تعداد کپی
            if count > 1:
                tag = f"@{item['channel']}_Verified({count})"
            else:
                tag = f"@{item['channel']}"
            
            final_configs.append(f"{full_link.split('#')[0]}#{tag}")

    if not final_configs: return
    
    final_text = "\n".join(final_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
