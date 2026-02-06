import requests
import re
import base64
import html
import socket
from datetime import datetime

# تابع تستر داخلی
def is_port_open(link):
    try:
        server_info = re.search(r'@([^:/#?]+):(\d+)', link)
        if server_info:
            address = server_info.group(1)
            port = int(server_info.group(2))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(1.0)
                return s.connect_ex((address, port)) == 0
        return True 
    except:
        return False

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except: return

    configs = []
    
    # اصلاح شده: الگوی بدون پرانتز برای استخراج کامل لینک
    pattern = r'vless://[^\s<>"]+|vmess://[^\s<>"]+|trojan://[^\s<>"]+|ss://[^\s<>"]+|ssr://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            r = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=20)
            
            if r.status_code == 200:
                content = html.unescape(r.text)
                # استخراج لینک‌ها با الگوی اصلاح شده
                found_links = re.findall(pattern, content)
                
                for link in found_links[-15:]:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    
                    if is_port_open(clean_link):
                        if "#" in clean_link:
                            clean_link = clean_link.split("#")[0]
                        
                        configs.append(f"{clean_link}#@{clean_ch}_Verified")
        except:
            continue

    if not configs:
        print("No configs found. Check pattern or channel content.")
        return

    unique_configs = list(dict.fromkeys(configs))
    final_text = "\n".join(unique_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)
    print(f"Done! {len(unique_configs)} configs saved.")

if __name__ == "__main__":
    collect()
