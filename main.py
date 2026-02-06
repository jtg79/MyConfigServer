import requests
import re
import base64
import html

def collect():
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return

    configs = []
    # استفاده از ?: برای اینکه پرانتز کل لینک را خراب نکند
    pattern = r'(?:vless|vmess|trojan|ss|ssr|tuic|hy2|hysteria2)://[^\s<>"]+'

    for ch in channels:
        clean_ch = ch.replace('@', '').strip()
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            
            if response.status_code == 200:
                decoded_page = html.unescape(response.text)
                found_links = re.findall(pattern, decoded_page)
                
                # فقط ۱۰ مورد آخر
                latest = found_links[-10:] if len(found_links) > 10 else found_links
                
                for link in latest:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    
                    if "#" in clean_link:
                        clean_link = clean_link.split("#")[0]
                    
                    # حالا لینک کامل + اسم کانال
                    final_link = f"{clean_link}#@{clean_ch}"
                    configs.append(final_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        return

    final_content = "\n".join(unique_configs)
    encoded_content = base64.b64encode(final_content.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(encoded_content)

if __name__ == "__main__":
    collect()
