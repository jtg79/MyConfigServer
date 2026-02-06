import requests
import re
import base64
import html

def collect():
    with open('channels.txt', 'r') as f:
        channels = [line.strip() for line in f if line.strip()]
    
    configs = []
    # حذف پرانتز اضافی برای استخراج کل لینک
    pattern = r'vless://[^\s<>"]+|vmess://[^\s<>"]+|trojan://[^\s<>"]+|ss://[^\s<>"]+|ssr://[^\s<>"]+|hy2://[^\s<>"]+|hysteria2://[^\s<>"]+'

    for ch in channels:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://t.me/s/{ch}", headers=headers, timeout=15)
            if r.status_code == 200:
                decoded_text = html.unescape(r.text)
                found = re.findall(pattern, decoded_text)
                for link in found:
                    # تمیزکاری نهایی
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    configs.append(clean_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        print("هیچ لینکی پیدا نشد.")
        return

    # تبدیل به متن و Base64
    final_text = "\n".join(unique_configs)
    base64_string = base64.b64encode(final_text.encode("utf-8")).decode("ascii")
    
    with open('sub_link.txt', 'w') as f:
        f.write(base64_string)

if __name__ == "__main__":
    collect()
