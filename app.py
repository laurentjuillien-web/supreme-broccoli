import streamlit as st
import pandas as pd
import yfinance as yf
import pandas_ta as ta

st.set_page_config(page_title="Scan Boursier Hebdo", layout="wide")

st.title("📈 Mon Radar Boursier & Plan de Trade")
st.markdown("Analyse automatique des rebonds sur supports hebdomadaires (CAC 40 / SRD).")

# Bouton pour lancer le scan à la demande
if st.button("🚀 Lancer le scan du marché", type="primary"):
    
    tickers = [
        "AIR.PA", "BNP.PA", "DG.PA", "OR.PA", "SAN.PA", "TTE.PA", "CAP.PA", "GLE.PA",
        "ACA.PA", "AI.PA", "BN.PA", "CA.PA", "DSY.PA", "EL.PA", "EN.PA",
        "ENGI.PA", "KER.PA", "LR.PA", "MC.PA", "ORA.PA", "PUB.PA", "RI.PA",
        "RMS.PA", "RNO.PA", "SAF.PA", "SGO.PA", "STLA.PA", "STM.PA", "SU.PA", "VIE.PA", "VIV.PA"
    ]

    results = []
    progress_text = st.empty()
    progress_bar = st.progress(0)

    total = len(tickers)
    for i, ticker in enumerate(tickers):
        progress_text.text(f"Analyse en cours : {ticker} ({i+1}/{total})")
        progress_bar.progress((i + 1) / total)
        
        try:
            stock = yf.Ticker(ticker)
            df_daily = stock.history(period="1y", interval="1d")
            df_weekly = stock.history(period="2y", interval="1wk")
            
            if len(df_daily) < 50 or len(df_weekly) < 20:
                continue
                
            df_daily['RSI'] = ta.rsi(df_daily['Close'], length=14)
            df_daily['Vol_SMA20'] = ta.sma(df_daily['Volume'], length=20)
            
            macd = ta.macd(df_daily['Close'])
            df_daily['MACD'] = macd.iloc[:, 0]
            df_daily['MACD_Signal'] = macd.iloc[:, 1]
            df_daily['MACD_Hist'] = macd.iloc[:, 2]

            weekly_support = df_weekly['Low'].tail(20).min()
            weekly_resistance = df_weekly['High'].tail(20).max()
            
            last = df_daily.iloc[-1]
            prev = df_daily.iloc[-2]
            
            dist_support_pct = ((last['Close'] - weekly_support) / weekly_support) * 100
            
            if 0 <= dist_support_pct <= 6.0:
                stop_loss = round(weekly_support * 0.985, 2)
                
                is_green_candle = last['Close'] > last['Open']
                is_rsi_rising = last['RSI'] > prev['RSI']
                is_near_exact_support = dist_support_pct <= 1.5
                
                if (is_green_candle and is_rsi_rising) or (is_near_exact_support and is_green_candle):
                    statut = "🟢 ACHAT (Rebond confirmé)"
                else:
                    statut = "🔴 ATTENDRE (En approche / Baisse)"
                
                results.append({
                    "Ticker": ticker,
                    "Prix (€)": round(last['Close'], 2),
                    "Support W (€)": round(weekly_support, 2),
                    "Dist. Supp (%)": round(dist_support_pct, 2),
                    "Stop-Loss (€)": stop_loss,
                    "Cible (€)": round(weekly_resistance, 2),
                    "Statut": statut
                })
        except Exception:
            continue

    progress_text.empty()
    progress_bar.empty()

    df_res = pd.DataFrame(results)
    if not df_res.empty:
        st.success("Scan terminé avec succès !")
        st.dataframe(df_res.sort_values(by="Dist. Supp (%)"), use_container_width=True)
    else:
        st.warning("Aucune action en approche de support pour le moment.")
else:
    st.info("Clique sur le bouton ci-dessus pour actualiser les données du marché en direct.")
