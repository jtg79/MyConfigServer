import requests
import re
import base64
import html

def collect():
    with open('channels.txt', 'r') as f:
        channels = [line.strip() for line in f if line.strip()]
    
    configs = []
    # الگوی دقیق برای پروتکل‌ها
    pattern = r'(vless|vmess|trojan|ss|ssr|tuic|hysteria2|hysteria)://[^\s<>"]+'

    for ch in channels:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://t.me/s/{ch}", headers=headers, timeout=15)
            if r.status_code == 200:
                decoded_text = html.unescape(r.text)
                found = re.findall(pattern, decoded_text)
                for link in found:
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    configs.append(clean_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        return

    # ۱. ترکیب لینک‌ها با اینتر (بدون هیچ فاصله اضافی)
    final_text = "\n".join(unique_configs)
    
    # ۲. تبدیل به بایت و سپس انکود کردن
    sample_string_bytes = final_text.encode("ascii", "ignore")
    base64_bytes = base64.b64encode(sample_string_bytes)
    base64_string = base64_bytes.decode("ascii")
    
    # ۳. حذف هرگونه کاراکتر اینتر یا فاصله از کل متن Base64 (بسیار مهم برای v2rayN)
    base64_string = base64_string.replace("\n", "").replace("\r", "").replace(" ", "")

    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
