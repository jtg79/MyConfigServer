import requests
import re
import base64
import html
import socket
from datetime import datetime, timedelta

# تابع تستر داخلی برای بررسی زنده بودن پورت سرور
def is_port_open(link):
    try:
        # استخراج آدرس و پورت از لینک (معمولاً بعد از @ و قبل از #)
        server_info = re.search(r'@([^:/]+):(\d+)', link)
        if server_info:
            address = server_info.group(1)
            port = int(server_info.group(2))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.5) # مهلت تست ۱.۵ ثانیه
                return s.connect_ex((address, port)) == 0
        return True # اگر فرمت آدرس شناسایی نشد، حذفش نمی‌کنیم
    except:
        return False

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    configs = []
    pattern = r'vless://[^\s<>"]+|vmess://[^\s<>"]+|trojan://[^\s<>"]+|ss://[^\s<>"]+|ssr://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'
    
    # دریافت تاریخ امروز و دیروز به فرمت تلگرام
    today = datetime.now().strftime("%B %d")
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%B %d")

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            
            if r.status_code == 200:
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                
                ch_today = []
                ch_yesterday = []
                
                for msg in messages:
                    # پیدا کردن تمام لینک‌های داخل این پیام
                    found = re.findall(pattern, html.unescape(msg))
                    if today in msg:
                        ch_today.extend(found)
                    elif yesterday in msg:
                        ch_yesterday.extend(found)
                
                # انتخاب ۵ تای آخر دیروز و ۱۰ تای آخر امروز
                selected_links = ch_yesterday[-5:] + ch_today[-10:]
                
                for link in selected_links:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    
                    # مرحله تست زنده بودن پورت
                    if is_port_open(clean_link):
                        if "#" in clean_link:
                            clean_link = clean_link.split("#")[0]
                        
                        # اضافه کردن نام کانال و برچسب تایید
                        final_link = f"{clean_link}#@{clean_ch}_Verified"
                        configs.append(final_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        print("هیچ کانفیگ جدید و سالمی یافت نشد.")
        return

    final_text = "\n".join(unique_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
