name: Actualizar precios diarios

on:
  schedule:
    - cron: '0 12 * * 1-5'
  workflow_dispatch:

jobs:
  update:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Python setup
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Instalar dependencias
        run: pip install yfinance requests

      - name: Actualizar precios
        run: python update_prices.py

      - name: Commit cambios
        run: |
          git config user.name "Investment Radar Bot"
          git config user.email "bot@pergolesi.com"
          git add index.html
          git diff --staged --quiet || git commit -m "Auto-update precios $(date +'%d/%m/%Y %H:%M')"
          git push

      - name: Deploy a Cloudflare Pages
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          python - <<'PYEOF'
          import requests, os, zipfile, io

          token = os.environ['CLOUDFLARE_API_TOKEN']
          account_id = os.environ['CLOUDFLARE_ACCOUNT_ID']
          project = 'radarinversionesestudiopergolesi'

          buf = io.BytesIO()
          with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as z:
              z.write('index.html')
          buf.seek(0)

          url = f'https://api.cloudflare.com/client/v4/accounts/{account_id}/pages/projects/{project}/deployments'
          headers = {'Authorization': f'Bearer {token}'}
          files = {'file': ('index.html.zip', buf, 'application/zip')}
          r = requests.post(url, headers=headers, files=files)
          data = r.json()
          if data.get('success'):
              print('Deploy exitoso:', data['result'].get('url', ''))
          else:
              print('Error:', data.get('errors'))
              exit(1)
          PYEOF
