#!/usr/bin/env python3
"""
Actualiza precios en index.html usando Yahoo Finance.
Corre automaticamente via GitHub Actions todos los dias de semana.
"""

import yfinance as yf
import re
from datetime import datetime

TICKERS = [
    "GOOGL","MSFT","NVDA","AVGO","META","AMZN","TSM","ASML","BRKB","COST",
    "V","MA","INTU","NOW","ANET","PANW","CRWD","MELI","LLY","AMAT","LRCX",
    "KLAC","QCOM","CEG","BX","PLTR","ARM","MU","WDC","VRT","APP",
    "NET","DDOG","TTD","SNOW","CAVA","DUOL","DECK","RACE","KO","PG","JNJ",
    "WMT","MCD","PEP","CL","JPM","BLK","UNH","ADBE","CRM","TXN","MRVL",
    "FDX","DRI","GS","MS","CME","SPGI","MCO","AXP","MDB","MNDY","GTLB",
    "TDG","HEI","HWM","GE","ETN","TT","PWR","FIX","HII","NVO","REGN",
    "VRTX","ISRG","SYK","BSX","MEDP","RMD","CMG","LULU","BKNG","ABNB",
    "INTC","GLW","AMD",
    "SPY","QQQ","SMH","CIBR","URA","GLD","XLF","XLE","DIA","EWZ","IWM","EEM"
]

def fetch_prices():
    print(f"Descargando {len(TICKERS)} tickers de Yahoo Finance...")
    prices = {}
    batch_size = 20
    for i in range(0, len(TICKERS), batch_size):
        batch = TICKERS[i:i+batch_size]
        try:
            data = yf.download(batch, period="2d", interval="1d", progress=False, auto_adjust=True)
            if len(batch) == 1:
                t = batch[0]
                if not data.empty:
                    val = data['Close'].dropna().iloc[-1]
                    if float(val) > 0:
                        prices[t] = round(float(val), 2)
            else:
                for t in batch:
                    try:
                        if ('Close', t) in data.columns:
                            val = data['Close'][t].dropna().iloc[-1]
                            if float(val) > 0:
                                prices[t] = round(float(val), 2)
                        elif t in data['Close'].columns:
                            val = data['Close'][t].dropna().iloc[-1]
                            if float(val) > 0:
                                prices[t] = round(float(val), 2)
                    except Exception as e:
                        print(f"  Error {t}: {e}")
        except Exception as e:
            print(f"  Error batch {batch[:3]}: {e}")
    print(f"✓ {len(prices)} precios obtenidos")
    return prices

def update_html(prices):
    with open('index.html', 'r', encoding='utf-8') as f:
        html = f.read()

    updated = 0
    for ticker, new_price in prices.items():
        pattern = r'(\{t:"' + re.escape(ticker) + r'"[^}]*?,p:)([\d.]+)'
        def replace_price(m, np=new_price):
            return m.group(1) + str(np)
        new_html, count = re.subn(pattern, replace_price, html)
        if count > 0:
            html = new_html
            updated += 1

    # Recalculate upside for each ticker
    for ticker, new_price in prices.items():
        # Find target for this ticker
        target_match = re.search(r't:"' + re.escape(ticker) + r'"[^}]*?,p:[\d.]+,target:([\d.]+),upside:([-\d.]+)', html)
        if target_match:
            target = float(target_match.group(1))
            new_upside = round((target - new_price) / new_price, 4)
            old_upside = target_match.group(2)
            html = html.replace(f',upside:{old_upside},', f',upside:{new_upside},', 1)

    # Update date in footer
    today = datetime.now().strftime('%d/%m/%Y')
    html = re.sub(r'datos al \d{2}/\d{2}/\d{4}', f'datos al {today}', html)

    with open('index.html', 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✓ {updated} precios actualizados en index.html")
    print(f"✓ Fecha actualizada: {today}")
    return updated

if __name__ == "__main__":
    print("=" * 50)
    print(f"Investment Radar — Auto-update")
    print(f"Fecha: {datetime.now().strftime('%d/%m/%Y %H:%M UTC')}")
    print("=" * 50)
    prices = fetch_prices()
    if not prices:
        print("ERROR: Sin precios")
        exit(1)
    update_html(prices)
    print("=" * 50)
    print("✅ Completado")
