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
            after_at = link.split('@')[1]
            server_info = re.search(r'([^:/#?]+):(\d+)', after_at)
            if server_info:
                address = server_info.group(1)
                port = int(server_info.group(2))
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                    s.settimeout(1.2)
                    return s.connect_ex((address, port)) == 0
        return False 
    except:
        return False

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except: return

    configs = []
    
    # الگوی تخت و اصلاح‌شده (بدون پرانتز برای استخراج کامل لینک)
    pattern = r'vless://[^\s<>"]+|trojan://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            
            if r.status_code == 200:
                content = html.unescape(r.text)
                found_links = re.findall(pattern, content)
                
                # بررسی ۱۰ تای آخر هر کانال
                for link in found_links[-10:]:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    
                    if is_port_open(clean_link):
                        # شرط امنیتی برای Vless
                        if "vless" in clean_link and "security=" not in clean_link:
                            continue
                            
                        # حذف تگ‌های قبلی و اضافه کردن فقط نام کانال
                        base_link = clean_link.split("#")[0] if "#" in clean_link else clean_link
                        configs.append(f"{base_link}#@{clean_ch}")
        except:
            continue

    if not configs:
        return

    unique_configs = list(dict.fromkeys(configs))
    final_text = "\n".join(unique_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
