import json
import os
import sys

import django

# Ensure project root is on sys.path so settings module can be imported
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'topstyle_business.settings')
django.setup()

from django.test import Client

client = Client()
# Use a host allowed by settings to avoid DisallowedHost during test client requests
resp = client.get('/api/customize-products/', HTTP_HOST='localhost')
print('status:', resp.status_code)
try:
    content = resp.content.decode('utf-8')
    print(content)
    data = json.loads(content)
    print('count:', data.get('count'))
    if data.get('count'):
        for p in data.get('products', [])[:10]:
            print('-', p.get('id'), p.get('name'), p.get('image_url'))
except Exception as e:
    print('Error decoding response:', e)
    print(resp.content)
