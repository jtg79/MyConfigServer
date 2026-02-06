import requests
import re
import base64
import html

def collect_configs():
    with open('channels.txt', 'r') as f:
        channels = [line.strip() for line in f if line.strip()]
    
    configs = []
    # الگوی پیشرفته برای شکار لینک‌ها و نادیده گرفتن متن‌های اطراف، نقل‌قول‌ها و تگ‌های HTML
    pattern = r'(vless|vmess|trojan|ss|ssr|tuic|hysteria2|hysteria)://[^\s<>"]+'

    for ch in channels:
        try:
            # دریافت نسخه وب کانال
            r = requests.get(f"https://t.me/s/{ch}", timeout=15)
            if r.status_code == 200:
                # تبدیل کدهای HTML مثل &amp; به کاراکترهای واقعی
                decoded_text = html.unescape(r.text)
                
                found = re.findall(pattern, decoded_text)
                for link in found:
                    # تمیزکاری نهایی: حذف کاراکترهای احتمالی مزاحم در انتهای لینک
                    clean_link = link.strip().split('<')[0].split('"')[1] if '"' in link else link.strip().split('<')[0]
                    
                    # اضافه کردن تگ نام کانال برای شناسایی در اپلیکیشن
                    if "#" in clean_link:
                        clean_link = clean_link.split("#")[0]
                    
                    final_link = f"{clean_link}#{ch}_Auto"
                    configs.append(final_link)
        except Exception as e:
            print(f"Error in {ch}: {e}")

    # حذف تکراری‌ها
    unique_configs = list(dict.fromkeys(configs))
    
    # خروجی متنی برای بررسی (اختیاری) و نسخه Base64
    final_text = "\n".join(unique_configs)
    encoded = base64.b64encode(final_text.encode('utf-8')).decode('utf-8')
    
    with open('sub_link.txt', 'w') as f:
        f.write(encoded)
    
    print(f"Done! {len(unique_configs)} configs collected.")

if __name__ == "__main__":
    collect_configs()
