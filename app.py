import streamlit as st
import pandas as pd
import yfinance as yf

st.set_page_config(page_title="Scan Boursier Hebdo", layout="wide")

st.title("📈 Mon Radar Boursier & Plan de Commerce")
st.markdown("Analyse automatique des rebonds sur supports hebdomadaires (CAC 40/SRD).")

if st.button("🚀 Lancer le scan du marché", type="primary"):
    
    tickers = [
        "AIR.PA", "BNP.PA", "DG.PA", "OR.PA", "SAN.PA", "TTE.PA", "CAP.PA", "GLE.PA",
        "ACA.PA", "AI.PA", "BN.PA", "CA.PA", "DSY.PA", "EL.PA", "EN.PA",
        "ENGI.PA", "KER.PA", "LR.PA", "MC.PA", "ORA.PA", "PUB.PA", "RI.PA",
        "RMS.PA", "RNO.PA", "SAF.PA", "SGO.PA", "STLA.PA", "STM.PA", "SU.PA", "VIE.PA", "VIV.PA"
    ]
    
    results = []
    text_prog = st.empty()
    progress_bar = st.progress(0)
    
    total = len(tickers)
    for i, ticker in enumerate(tickers):
        text_prog.text(f"Analyse en cours : {ticker} ({i+1}/{total})")
        progress_bar.progress((i + 1) / total)
        
        try:
            stock = yf.Ticker(ticker)
            df_daily = stock.history(period="1 an", interval="1d")
            df_weekly = stock.history(period="2 ans", interval="1wk")
            
            if len(df_daily) < 50 or len(df_weekly) < 20:
                continue
                
            # Calcul RSI simple maison (sans pandas_ta)
            delta = df_daily['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df_daily['RSI'] = 100 - (100 / (1 + rs))
            
            df_daily['Vol_SMA20'] = df_daily['Volume'].rolling(window=20).mean()
            
            support_hebdo = df_weekly['Low'].rolling(window=20).min().iloc[-1]
            resistance_hebdo = df_weekly['High'].rolling(window=20).max().iloc[-1]
            
            dernier = df_daily.iloc[-1]
            precedent = df_daily.iloc[-2]
            
            # Condition simple de rebond sur support
            if dernier['Close'] >= support_hebdo * 0.99 and dernier['Close'] <= support_hebdo * 1.03:
                results.append({
                    "Ticker": ticker,
                    "Prix Actuel": round(dernier['Close'], 2),
                    "Support Hebdo": round(support_hebdo, 2),
                    "RSI (14)": round(dernier['RSI'], 1),
                    "Volume / Moy20": round(dernier['Volume'] / dernier['Vol_SMA20'], 2) if dernier['Vol_SMA20'] > 0 else 0
                })
        except Exception as e:
            continue
            
    progress_bar.empty()
    text_prog.empty()
    
    if results:
        df_res = pd.DataFrame(results)
        st.success(f"Scan terminé ! {len(results)} opportunité(s) détectée(s).")
        st.dataframe(df_res, use_container_width=True)
    else:
        st.info("Aucune configuration de rebond exacte détectée aujourd'hui sur ces critères.")
