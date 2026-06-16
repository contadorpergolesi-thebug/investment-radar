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
        run: python deploy_cloudflare.py
