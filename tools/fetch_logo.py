import urllib.request
import re

url = 'https://www.ncdmb.gov.ng/'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
req = urllib.request.Request(url, headers=headers)
try:
    with urllib.request.urlopen(req, timeout=10) as response:
        html = response.read().decode('utf-8', errors='ignore')
        logos = re.findall(r'src=["\']([^"\']*(?:logo|brand|crest)[^"\']*\.(?:png|jpg|jpeg|svg|webp))["\']', html, re.I)
        print('Found logos:', logos[:10])
except Exception as e:
    print('Error fetching:', e)
