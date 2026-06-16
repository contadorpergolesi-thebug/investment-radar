#!/usr/bin/env python3
"""
Deploy index.html a Cloudflare Pages via API.
"""
import requests
import os
import zipfile
import io

token = os.environ['CLOUDFLARE_API_TOKEN']
account_id = os.environ['CLOUDFLARE_ACCOUNT_ID']
project = 'radarinversionesestudiopergolesi'

print(f"Desplegando a Cloudflare Pages: {project}")

# Crear zip con index.html
buf = io.BytesIO()
with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
    z.write('index.html')
buf.seek(0)

# Upload a Cloudflare Pages
url = f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project}/deployments'
headers = {'Authorization': f'Bearer {token}'}
files = {'file': ('project.zip', buf, 'application/zip')}

r = requests.post(url, headers=headers, files=files)
data = r.json()

if data.get('success'):
    deploy_url = data['result'].get('url', '')
    print(f"Deploy exitoso: {deploy_url}")
else:
    print(f"Error en deploy: {data.get('errors')}")
    exit(1)
