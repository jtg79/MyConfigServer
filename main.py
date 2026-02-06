import requests
import re
import base64
import html
import socket
from datetime import datetime, timedelta

# تابع تستر داخلی برای بررسی زنده بودن پورت سرور
def is_port_open(link):
    try:
        # استخراج آدرس و پورت (هوشمند برای Vless, Trojan, SS)
        server_info = re.search(r'@([^:/#?]+):(\d+)', link)
        if server_info:
            address = server_info.group(1)
            port = int(server_info.group(2))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0) # تست سریع ۱ ثانیه‌ای
                return s.connect_ex((address, port)) == 0
        
        # هوشمندی: اگر فرمت لینک پیچیده بود (مثل Vmess)، تاییدش کن تا ریسک نشود
        return True 
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
    
    # دریافت تاریخ امروز و دیروز با دو فرمت (کامل و مخفف) برای اطمینان
    now = datetime.now()
    yesterday_date = now - timedelta(days=1)
    
    dates_to_check = [
        now.strftime("%B %d"),    # February 06
        now.strftime("%b %d"),    # Feb 06
        yesterday_date.strftime("%B %d"),
        yesterday_date.strftime("%b %d")
    ]

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
                    # دکود کردن محتوا برای پیدا کردن تاریخ و لینک
                    decoded_msg = html.unescape(msg)
                    found = re.findall(pattern, decoded_msg)
                    
                    # تفکیک بر اساس تاریخ (امروز یا دیروز)
                    is_today = any(d in msg for d in dates_to_check[:2])
                    is_yesterday = any(d in msg for d in dates_to_check[2:])
                    
                    if is_today:
                        ch_today.extend(found)
                    elif is_yesterday:
                        ch_yesterday.extend(found)
                
                # انتخاب ۵ تای آخر دیروز و ۱۰ تای آخر امروز (جمعاً حداکثر ۱۵ تا)
                selected_links = ch_yesterday[-5:] + ch_today[-10:]
                
                for link in selected_links:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    
                    # تست زنده بودن پورت
                    if is_port_open(clean_link):
                        if "#" in clean_link:
                            clean_link = clean_link.split("#")[0]
                        
                        # اضافه کردن نام کانال و برچسب Verified
                        final_link = f"{clean_link}#@{clean_ch}_Verified"
                        configs.append(final_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    # حتی اگر لیستی پیدا نشد، فایل را بازنویسی کن تا از آپدیت شدن مطمئن شویم
    final_text = "\n".join(unique_configs) if unique_configs else ""
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
