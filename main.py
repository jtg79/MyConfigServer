import requests
import re
import base64
import html

def collect():
    # ۱. خواندن لیست کانال‌ها
    try:
        with open('channels.txt', 'r') as f:
            channels = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("فایل channels.txt پیدا نشد!")
        return

    configs = []
    # الگوی جامع برای تمام پروتکل‌های معتبر
    pattern = r'(vless|vmess|trojan|ss|ssr|tuic|hy2|hysteria2)://[^\s<>"]+'

    for ch in channels:
        # پاک‌سازی نام کانال از @ احتمالی برای استفاده در آدرس تلگرام
        clean_ch = ch.replace('@', '').strip()
        try:
            # استفاده از User-Agent برای شبیه‌سازی مرورگر و جلوگیری از بلاک شدن
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
            response = requests.get(f"https://t.me/s/{clean_ch}", headers=headers, timeout=15)
            
            if response.status_code == 200:
                # تبدیل کدهای HTML به متن معمولی (مثلاً &amp; به &)
                decoded_page = html.unescape(response.text)
                found_links = re.findall(pattern, decoded_page)
                
                # انتخاب حداکثر ۱۰ مورد آخر هر کانال
                latest = found_links[-10:] if len(found_links) > 10 else found_links
                
                for link in latest:
                    # تمیزکاری نهایی لینک
                    clean_link = link.strip().split('<')[0].split('"')[0].split("'")[0]
                    
                    # حذف هرگونه Remark قدیمی و جایگزینی با نام کانال شما
                    if "#" in clean_link:
                        clean_link = clean_link.split("#")[0]
                    
                    # چسباندن نام کانال به عنوان نام کانفیگ
                    final_link = f"{clean_link}#@{clean_ch}"
                    configs.append(final_link)
        except Exception as e:
            print(f"خطا در دریافت از کانال {clean_ch}: {e}")
            continue

    # حذف لینک‌های تکراری
    unique_configs = list(dict.fromkeys(configs))
    
    if not unique_configs:
        print("هیچ کانفیگی یافت نشد!")
        return

    # آماده‌سازی متن نهایی و تبدیل به Base64
    final_content = "\n".join(unique_configs)
    encoded_content = base64.b64encode(final_content.encode("utf-8")).decode("ascii")
    
    # ذخیره در فایل خروجی
    with open('sub_link.txt', 'w') as f:
        f.write(encoded_content)
    
    print(f"عملیات با موفقیت انجام شد. {len(unique_configs)} کانفیگ جمع‌آوری شد.")

if __name__ == "__main__":
    collect()
