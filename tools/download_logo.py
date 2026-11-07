import urllib.request
import os

logo_url = 'https://www.ncdmb.gov.ng/wp-content/uploads/2020/12/ncdmdbsite_logo-2-removebg-preview-new.png'
dest_path = r'C:\Users\hp\Desktop\NCMB\static\images\logo.png'
backup_path = r'C:\Users\hp\Desktop\NCMB\static\images\ncdmb_logo.png'

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
req = urllib.request.Request(logo_url, headers=headers)

try:
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = resp.read()
        with open(dest_path, 'wb') as f:
            f.write(data)
        with open(backup_path, 'wb') as f:
            f.write(data)
        print(f"Successfully downloaded NCDMB logo ({len(data)} bytes) to {dest_path}")
except Exception as e:
    print(f"Error downloading logo: {e}")
