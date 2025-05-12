
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Dashboard de Ausentismo", layout="wide")
st.title("📊 Dashboard de Ausentismo Laboral")

# Cargar datos limpios
@st.cache_data
def cargar_datos():
    df = pd.read_excel("data_limpia_final.xlsx")
    df['INCAPACIDAD - FECHA DE INICIO'] = pd.to_datetime(df['INCAPACIDAD - FECHA DE INICIO'], errors='coerce')
    df['AÑO'] = df['INCAPACIDAD - FECHA DE INICIO'].dt.year
    return df

df = cargar_datos()

# Filtro por año
anios = sorted(df['AÑO'].dropna().unique())
opciones_anio = ["Todos los años"] + list(anios)
año_seleccionado = st.sidebar.selectbox("Selecciona un año", opciones_anio)

if año_seleccionado == "Todos los años":
    df_anio = df.copy()
else:
    df_anio = df[df['AÑO'] == año_seleccionado]

# Indicadores
col1, col2 = st.columns(2)
with col1:
    dias_prom = df_anio.groupby('C.C COLABORADOR')['INCAPACIDAD - DIAS'].sum().mean()
    st.metric("📅 Días promedio por colaborador", f"{dias_prom:.2f}")
with col2:
    costo_total = df_anio['COSTO INCAPACIDAD'].sum()
    st.metric("💸 Costo total estimado", f"${costo_total:,.0f}")

# Comparativa entre años
if año_seleccionado != "Todos los años" and año_seleccionado > min(anios):
    prev_year = año_seleccionado - 1
    if prev_year in anios:
        df_prev = df[df['AÑO'] == prev_year]
        dias_prev = df_prev.groupby('C.C COLABORADOR')['INCAPACIDAD - DIAS'].sum().mean()
        costo_prev = df_prev['COSTO INCAPACIDAD'].sum()
        col1.metric("🔁 Comparado con año anterior (días)", f"{dias_prom - dias_prev:.2f}", delta=f"{dias_prom - dias_prev:.2f}")
        col2.metric("🔁 Comparado con año anterior (costo)", f"${costo_total - costo_prev:,.0f}", delta=f"${costo_total - costo_prev:,.0f}")

# Diagnósticos más frecuentes
st.subheader("🧾 Top 10 Diagnósticos Más Comunes")
top_diag = df_anio['INCAPACIDAD - TIPO DE GENERACIÓN'].value_counts().head(10)
st.bar_chart(top_diag)

# Diagnósticos con más días acumulados
st.subheader("📅 Diagnósticos con más días acumulados")
top_dias_diag = df_anio.groupby('INCAPACIDAD - TIPO DE GENERACIÓN')['INCAPACIDAD - DIAS'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_dias_diag)

# Diagnósticos con mayor impacto económico
st.subheader("💰 Diagnósticos con mayor costo acumulado")
top_cost_diag = df_anio.groupby('INCAPACIDAD - TIPO DE GENERACIÓN')['COSTO INCAPACIDAD'].sum().sort_values(ascending=False).head(10)
st.bar_chart(top_cost_diag)

# Alertas más frecuentes
st.subheader("🚨 Alertas más frecuentes")
alert_cols = [col for col in df.columns if 'ALERTA' in col and col != 'NUM ALERTAS']
alerta_totales = df_anio[alert_cols].sum().sort_values(ascending=False)
st.bar_chart(alerta_totales)

# Top colaboradores con más incapacidades
st.subheader("👥 Top 10 colaboradores con más incapacidades")
top_colabs = df_anio['C.C COLABORADOR'].value_counts().head(10).rename_axis('Colaborador').reset_index(name='Nº Incapacidades')
st.dataframe(top_colabs)

# Exportar datos filtrados
st.subheader("📥 Exportar datos filtrados")
csv = df_anio.to_csv(index=False).encode('utf-8')
st.download_button("Descargar CSV", data=csv, file_name="datos_filtrados.csv", mime="text/csv")

st.caption("Desarrollado como parte de una prueba técnica para Uell. © 2024")
