import requests
import re
import base64
import html
import socket
from datetime import datetime

def get_config_identity(link):
    """استخراج شناسه هوشمند: UUID برای VLESS، و آدرس برای بقیه"""
    try:
        if link.startswith('vless://'):
            # استخراج محتوای بین // و @
            match = re.search(r'vless://([^@]+)@', link)
            if match:
                return f"VLESS_ID:{match.group(1)}"
        
        # برای بقیه پروتکل‌ها: استخراج آدرس و پورت
        if '@' in link:
            server_part = link.split('@')[1].split('/')[0].split('?')[0].split('#')[0]
            return f"SERVER_ID:{server_part}"
    except:
        return None
    return None

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
    # پترن فیکس شده و تخت
    pattern = r'vless://[^\s<>"]+|trojan://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'

    for ch in channels:
        try:
            clean_ch = ch.replace('@', '').strip()
            r = requests.get(f"https://t.me/s/{clean_ch}", headers={'User-Agent': 'Mozilla/5.0'}, timeout=15)
            if r.status_code == 200:
                messages = r.text.split('<div class="tgme_widget_message_wrap')
                for msg in messages:
                    time_match = re.search(r'datetime="([^"]+)"', msg)
                    if time_match:
                        timestamp = time_match.group(1)
                        decoded_msg = html.unescape(msg)
                        links = re.findall(pattern, decoded_msg)
                        
                        for link in links[-20:]:
                            full_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                            config_id = get_config_identity(full_link)
                            
                            if config_id:
                                all_raw_data.append({
                                    'id': config_id,
                                    'full': full_link,
                                    'time': timestamp,
                                    'channel': clean_ch
                                })
        except: continue

    # ۱. مرتب‌سازی زمانی (قدیمی‌ترین اول)
    all_raw_data.sort(key=lambda x: x['time'])

    # ۲. تحلیل کپی‌رایت کانال‌ها
    first_publishers = {} 
    occurrence_count = {}

    for item in all_raw_data:
        c_id = item['id']
        occurrence_count[c_id] = occurrence_count.get(c_id, 0) + 1
        if c_id not in first_publishers:
            first_publishers[c_id] = item['channel']

    final_configs = []
    processed_ids = set()

    # ۳. فیلتر نهایی و خروجی
    for item in all_raw_data:
        c_id = item['id']
        if c_id not in processed_ids and item['channel'] == first_publishers[c_id]:
            
            full_link = item['full']
            # فیلتر امنیتی Vless
            if "vless" in full_link and not any(s in full_link for s in ["security=tls", "security=reality"]):
                continue
            
            if is_port_open(full_link):
                processed_ids.add(c_id)
                
                # برچسب Verified برای منابعی که کپی شده‌اند
                is_copied = occurrence_count[c_id] > 1
                tag = f"@{item['channel']}_Verified" if is_copied else f"@{item['channel']}"
                
                base_link = full_link.split('#')[0]
                final_configs.append(f"{base_link}#{tag}")

    if not final_configs: return

    final_text = "\n".join(final_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
