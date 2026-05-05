import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# CONFIGURACIÓN CORPORATE TECH
st.set_page_config(
    page_title="PRO-BET V3 | Dashboard de Ingeniería",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Profesional Personalizado
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    </style>
    """, unsafe_allow_html=True)

def fetch_all_data():
    """
    Recupera el set completo de datos desde el Motor Avanzado.
    Incluye validación de integridad para evitar fallos en tiempo real.
    """
    try:
        # Endpoint unificado que consume de routers/avanzado.py y routers/odds.py
        api_url = "http://localhost:8000/api/v1/dashboard/full-stream"
        response = requests.get(api_url, timeout=2)
        if response.status_code == 200:
            return pd.DataFrame(response.json())
        return pd.DataFrame()
    except Exception:
        return pd.DataFrame()

def main():
    # BARRA LATERAL: CONTROL DE TIEMPO REAL
    with st.sidebar:
        st.title("⚙️ Engine Control")
        st.status("Conectado al Motor V3", state="running")
        refresh_rate = st.select_slider("Frecuencia de Actualización", options=[1, 2, 5, 10, 30], value=2)
        show_raw = st.checkbox("Mostrar Data Cruda (Debug)")
        st.divider()
        st.info("Silo: Geopolítica/Apuestas - Protocolo Estricto")

    # CABECERA DINÁMICA
    header_placeholder = st.empty()
    
    # CONTENEDORES DE DATOS (Muestra TODO lo que antes faltaba)
    metric_row = st.columns(4)
    main_table_placeholder = st.empty()
    analysis_row = st.columns(2)

    while True:
        df = fetch_all_data()
        
        with header_placeholder.container():
            st.title("⚡ Terminal de Datos en Tiempo Real")
            st.caption(f"Última actualización: {datetime.now().strftime('%H:%M:%S.%f')[:-3]}")

        if not df.empty:
            # 1. MÉTRICAS GLOBAL (TIEMPO REAL)
            metric_row[0].metric("Partidos Disponibles", len(df))
            metric_row[1].metric("Promedio Probabilidad", f"{df['prob_ensemble'].mean():.1%}")
            metric_row[2].metric("Oportunidades Kelly", len(df[df['kelly_fraction'] > 0]))
            metric_row[3].metric("Valor Promedio (EV)", f"{df['ev'].mean():.2f}")

            # 2. TABLA MAESTRA (TODOS LOS DATOS)
            with main_table_placeholder.container():
                st.subheader("🔥 Monitor de Oportunidades")
                # Columnas que antes no se veían y ahora son obligatorias
                display_cols = [
                    'hora', 'liga', 'local', 'visitante', 
                    'cuota_local', 'cuota_empate', 'cuota_visitante',
                    'prob_elo', 'prob_dixon', 'prob_ensemble', 
                    'kelly_fraction', 'ev'
                ]
                st.dataframe(
                    df[display_cols].style.background_gradient(subset=['ev'], cmap='RdYlGn'),
                    use_container_width=True,
                    height=400
                )

            # 3. ANÁLISIS DE MODELOS (ELO VS DIXON)
            with analysis_row[0]:
                st.subheader("📊 Discrepancia de Modelos")
                st.scatter_chart(df, x='prob_elo', y='prob_dixon', color='liga')
            
            with analysis_row[1]:
                st.subheader("💰 Gestión de Bankroll (Kelly)")
                st.bar_chart(df.set_index('local')['kelly_fraction'])

            if show_raw:
                st.divider()
                st.write("Datos Binarios de Entrada:", df)

        else:
            st.error("⚠️ Error de Sincronización: El motor de datos no está respondiendo.")
            st.button("Forzar Reinicio de Scraper")

        # LOGICA DE TIEMPO REAL
        time.sleep(refresh_rate)
        st.rerun()

if __name__ == "__main__":
    main()
