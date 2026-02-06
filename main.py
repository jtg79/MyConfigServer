import requests
import re
import base64
import html

def collect():
    with open('channels.txt', 'r') as f:
        channels = [line.strip() for line in f if line.strip()]
    
    configs = []
    # الگوی جامع برای تمام پروتکل‌ها
    pattern = r'(vless|vmess|trojan|ss|ssr|tuic|hysteria2|hysteria)://[^\s<>"]+'

    for ch in channels:
        try:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.get(f"https://t.me/s/{ch}", headers=headers, timeout=15)
            if r.status_code == 200:
                decoded_text = html.unescape(r.text)
                found = re.findall(pattern, decoded_text)
                for link in found:
                    # تمیزکاری دقیق لینک از کاراکترهای اضافی
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    # حذف Remarkهای قبلی و اضافه کردن Remark تمیز
                    if "#" in clean_link:
                        clean_link = clean_link.split("#")[0]
                    
                    final_link = f"{clean_link}#{ch}"
                    configs.append(final_link)
        except:
            continue

    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        return

    # ایجاد متن نهایی: هر لینک در یک خط کاملاً مجزا
    final_text = "\n".join(unique_configs) + "\n"
    
    # تبدیل به Base64 استاندارد بدون کاراکترهای مزاحم
    encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    
    with open('sub_link.txt', 'w') as f:
        f.write(encoded)

if __name__ == "__main__":
    collect()
