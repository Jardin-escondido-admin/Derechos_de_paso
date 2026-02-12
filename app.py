import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO

# === CONFIGURACIÓN DE PÁGINA ===
st.set_page_config(
    page_title="Derechos de Paso FIT-FSRR",
    page_icon="🚂",
    layout="wide"
)

# === ESTILOS ===
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=JetBrains+Mono:wght@400;500&display=swap');
    
    .stApp {
        font-family: 'DM Sans', sans-serif;
    }
    
    .main-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 2rem 2.5rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        border: 1px solid rgba(255,255,255,0.05);
    }
    .main-header h1 {
        color: #e2e8f0;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .main-header p {
        color: #94a3b8;
        font-size: 1rem;
        margin: 0.5rem 0 0 0;
    }
    
    .metric-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
    }
    .metric-card h3 {
        color: #64748b;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin: 0 0 0.5rem 0;
        font-weight: 500;
    }
    .metric-card .number {
        font-family: 'JetBrains Mono', monospace;
        font-size: 2rem;
        font-weight: 700;
        margin: 0;
    }
    .green { color: #059669; }
    .yellow { color: #d97706; }
    .red { color: #dc2626; }
    .blue { color: #2563eb; }
    
    .motivo-table {
        width: 100%;
        border-collapse: collapse;
        font-size: 0.9rem;
    }
    .motivo-table th {
        background: #1a1a2e;
        color: #e2e8f0;
        padding: 0.75rem 1rem;
        text-align: left;
        font-weight: 500;
    }
    .motivo-table td {
        padding: 0.6rem 1rem;
        border-bottom: 1px solid #e2e8f0;
    }
    .motivo-table tr:hover {
        background: #f1f5f9;
    }
    
    .login-container {
        max-width: 400px;
        margin: 5rem auto;
        padding: 2.5rem;
        background: white;
        border-radius: 16px;
        border: 1px solid #e2e8f0;
        box-shadow: 0 4px 24px rgba(0,0,0,0.06);
    }
    
    div[data-testid="stFileUploader"] {
        border: 2px dashed #cbd5e1;
        border-radius: 12px;
        padding: 1rem;
    }
</style>
""", unsafe_allow_html=True)

# === AUTENTICACIÓN ===
USUARIOS = {
    "karen": "fit2026",
    "Daniela": "fit2026",
}

def login():
    """Pantalla de login"""
    st.markdown("""
    <div style="text-align: center; margin-top: 3rem;">
        <h1 style="font-size: 3rem;">🚂</h1>
        <h2 style="color: #1a1a2e; font-weight: 700;">Derechos de Paso</h2>
        <p style="color: #64748b;">FIT - FSRR | Sistema de Cruce de Tarifas</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        st.markdown("---")
        usuario = st.text_input("👤 Usuario", placeholder="Ingresa tu usuario")
        contrasena = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
        
        if st.button("Iniciar sesión", use_container_width=True, type="primary"):
            if usuario in USUARIOS and USUARIOS[usuario] == contrasena:
                st.session_state["autenticado"] = True
                st.session_state["usuario"] = usuario
                st.rerun()
            else:
                st.error("Usuario o contraseña incorrectos")

def cerrar_sesion():
    """Cerrar sesión"""
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = ""
    st.rerun()

# === FUNCIONES DE PROCESAMIENTO ===
def procesar_datos(archivo_fit, archivo_carros, archivo_loco):
    """Procesa los 3 archivos y retorna resultados"""
    
    # PASO 1: Leer archivos
    df_fit = pd.read_excel(archivo_fit, sheet_name="UDEA", header=1)
    df_fsrr_carros = pd.read_excel(archivo_carros, header=1)
    df_fsrr_loco = pd.read_excel(archivo_loco, header=1)
    df_dist = pd.read_excel(archivo_fit, sheet_name="LISTAS", header=None, skiprows=4)
    
    # PASO 2: Renombrar columnas
    df_fit = df_fit.rename(columns={
        "Número Guía": "guia",
        "Fecha Guía": "fecha_guia",
        "Distancia": "distancia",
        "Origen de Paso": "origen",
        "Destino de Paso": "destino",
        "Tarifa": "tarifa_fit",
        "Total": "total_fit"
    })
    
    df_fsrr_loco = df_fsrr_loco.rename(columns={
        "Numero de guia": "guia",
        "Fecha de guia": "fecha_guia",
        "Distancias": "distancia",
        "Origen": "origen",
        "Destino": "destino",
        "Tarifa": "tarifa_fsrr",
        "Provisión": "provision_fsrr"
    })
    
    df_fsrr_carros = df_fsrr_carros.rename(columns={
        "Número de guía": "guia",
        "Fecha guía": "fecha_guia",
        "Distancia": "distancia",
        "Estación Origen (EO)": "origen",
        "Estación Destino (ED)": "destino",
        "Tarifa UdeA": "tarifa_fsrr",
        "Provisión": "provision_fsrr"
    })
    
    # PASO 3.5: Homologar tipos
    for df in [df_fit, df_fsrr_carros, df_fsrr_loco]:
        df["fecha_guia"] = df["fecha_guia"].astype(str)
        df["guia"] = df["guia"].astype(str)
        df["distancia"] = pd.to_numeric(df["distancia"], errors="coerce").round(3).astype(str)
    
    # PASO 3.6: Limpiar datos
    for df in [df_fit, df_fsrr_carros, df_fsrr_loco]:
        df["fecha_guia"] = df["fecha_guia"].str[:10]
        df["guia"] = df["guia"].str.replace(".0", "", regex=False)
    
    # Crear tráfico en FIT
    df_fit["trafico"] = df_fit["origen"].str.strip().str.title() + " - " + df_fit["destino"].str.strip().str.title()
    
    # Renombrar tráfico en FSRR
    df_fsrr_carros["trafico"] = df_fsrr_carros["Tráfico"].str.strip()
    df_fsrr_loco["trafico"] = df_fsrr_loco["Tráfico"].str.strip()
    
    # PASO 3.7: Crear equipo_fit
    df_fit["Número"] = df_fit["Número"].astype(str).str.replace(".0", "", regex=False).str.strip()
    df_fit["equipo_fit"] = df_fit["Inicial"].str.strip() + " " + df_fit["Número"].str.strip().str.zfill(6)
    df_fit["equipo_fit"] = df_fit["equipo_fit"].str.split().str.join(" ")
    
    # PASO 3.8: Estandarizar estaciones
    df_fsrr_carros["trafico"] = df_fsrr_carros["trafico"].str.replace(
        "Ing A Lir Arciniega", "Ing.A. Lira Arciniega", regex=False)
    df_fsrr_loco["Tráfico"] = df_fsrr_loco["Tráfico"].str.replace(
        "Ing A Lir Arciniega", "Ing.A. Lira Arciniega", regex=False)
    
    # PASO 3.9: Corregir distancias
    df_dist = df_dist[[6, 7, 8]]
    df_dist.columns = ["origen_dist", "destino_dist", "km_dist"]
    df_dist = df_dist.dropna(subset=["origen_dist", "destino_dist"])
    df_dist["origen_dist"] = df_dist["origen_dist"].str.strip().str.title()
    df_dist["destino_dist"] = df_dist["destino_dist"].str.strip().str.title()
    df_dist["trafico_dist"] = df_dist["origen_dist"] + " - " + df_dist["destino_dist"]
    df_dist["km_dist"] = pd.to_numeric(df_dist["km_dist"], errors="coerce").round(3).astype(str)
    
    mapa_dist = dict(zip(df_dist["trafico_dist"], df_dist["km_dist"]))
    mascara_nan = (df_fit["distancia"] == "nan") | (df_fit["distancia"] == "")
    dist_corregidas = mascara_nan.sum()
    df_fit.loc[mascara_nan, "distancia"] = df_fit.loc[mascara_nan, "trafico"].map(mapa_dist)
    
    # PASO 3.10: Corregir fechas
    mascara_fecha = (df_fit["fecha_guia"] == "00/00/0000") | (df_fit["fecha_guia"] == "nan")
    fechas_corregidas = mascara_fecha.sum()
    df_fit.loc[mascara_fecha, "fecha_guia"] = df_fit.loc[mascara_fecha, "Fecha"].astype(str).str[:10]
    
    # PASO 5: Cruce FIT vs FSRR Carros
    df_fit_carros = df_fit[df_fit["Clase"] != "LOCOMOTORA"].copy()
    llaves = ["guia", "fecha_guia", "distancia", "trafico"]
    
    cruce_carros = pd.merge(
        df_fit_carros, df_fsrr_carros,
        on=llaves, how="outer", indicator=True, suffixes=("_fit", "_fsrr")
    )
    
    # PASO 5.1: Segundo intento sin fecha
    solo_fit_1 = cruce_carros[cruce_carros["_merge"] == "left_only"].copy()
    solo_fsrr_1 = cruce_carros[cruce_carros["_merge"] == "right_only"].copy()
    match_1 = cruce_carros[cruce_carros["_merge"] == "both"].copy()
    
    cruce_2 = pd.merge(
        solo_fit_1[["guia", "fecha_guia", "distancia", "trafico", "tarifa_fit", "total_fit"]],
        solo_fsrr_1[["guia", "fecha_guia", "distancia", "trafico", "tarifa_fsrr", "provision_fsrr"]],
        on=["guia", "distancia", "trafico"], how="inner", suffixes=("_fit", "_fsrr")
    )
    
    cruce_2["tarifa_fit"] = pd.to_numeric(cruce_2["tarifa_fit"], errors="coerce")
    cruce_2["tarifa_fsrr"] = pd.to_numeric(cruce_2["tarifa_fsrr"], errors="coerce")
    cruce_2["diferencia_tarifa"] = cruce_2["tarifa_fit"] - cruce_2["tarifa_fsrr"]
    con_dif_2 = cruce_2[cruce_2["diferencia_tarifa"] != 0]
    sin_dif_2 = cruce_2[cruce_2["diferencia_tarifa"] == 0]
    
    # PASO 5B: Cruce FIT vs Locomotoras
    df_fsrr_loco["equipo"] = df_fsrr_loco["Equipo"].str.strip()
    df_fit_loco = df_fit[df_fit["Inicial"] == "FSRR"].copy()
    df_fit_loco["equipo"] = df_fit_loco["equipo_fit"]
    llaves_loco = ["equipo", "trafico", "distancia"]
    
    cruce_loco = pd.merge(
        df_fit_loco, df_fsrr_loco,
        on=llaves_loco, how="outer", indicator=True, suffixes=("_fit", "_fsrr")
    )
    
    solo_fit_loco = cruce_loco[cruce_loco["_merge"] == "left_only"].copy()
    solo_fsrr_loco = cruce_loco[cruce_loco["_merge"] == "right_only"].copy()
    
    # PASO 7: Comparar tarifas carros
    coincidencias = cruce_carros[cruce_carros["_merge"] == "both"].copy()
    coincidencias["tarifa_fit"] = pd.to_numeric(coincidencias["tarifa_fit"], errors="coerce")
    coincidencias["tarifa_fsrr"] = pd.to_numeric(coincidencias["tarifa_fsrr"], errors="coerce")
    coincidencias["provision_fsrr"] = pd.to_numeric(coincidencias["provision_fsrr"], errors="coerce")
    coincidencias["diferencia_tarifa"] = coincidencias["tarifa_fit"] - coincidencias["tarifa_fsrr"]
    con_diferencia = coincidencias[coincidencias["diferencia_tarifa"] != 0]
    sin_diferencia = coincidencias[coincidencias["diferencia_tarifa"] == 0]
    
    # PASO 7B: Comparar tarifas locomotoras
    coincidencias_loco = cruce_loco[cruce_loco["_merge"] == "both"].copy()
    coincidencias_loco["tarifa_fit"] = pd.to_numeric(coincidencias_loco["tarifa_fit"], errors="coerce")
    coincidencias_loco["tarifa_fsrr"] = pd.to_numeric(coincidencias_loco["tarifa_fsrr"], errors="coerce")
    coincidencias_loco["provision_fsrr"] = pd.to_numeric(coincidencias_loco["provision_fsrr"], errors="coerce")
    coincidencias_loco["diferencia_tarifa"] = coincidencias_loco["tarifa_fit"] - coincidencias_loco["tarifa_fsrr"]
    con_diferencia_loco = coincidencias_loco[coincidencias_loco["diferencia_tarifa"] != 0]
    sin_diferencia_loco = coincidencias_loco[coincidencias_loco["diferencia_tarifa"] == 0]
    
    # PASO 5.2: Tercer intento - sin guía
    sin_guia_fit = solo_fit_1[
        (solo_fit_1["guia"] == "0") | (solo_fit_1["guia"] == "nan") | (solo_fit_1["guia"] == "")
    ].copy()
    guias_match2 = set(cruce_2["guia"])
    sin_guia_fsrr = solo_fsrr_1[~solo_fsrr_1["guia"].isin(guias_match2)].copy()
    
    cruce_3 = pd.merge(
        sin_guia_fit,
        sin_guia_fsrr[["fecha_guia", "distancia", "trafico", "tarifa_fsrr", "provision_fsrr"]],
        on=["fecha_guia", "distancia", "trafico"], how="inner", suffixes=("_fit", "_fsrr")
    )
    cruce_3 = cruce_3.drop_duplicates(subset=["fecha_guia", "distancia", "trafico", "tarifa_fit"])
    cruce_3["tarifa_fit"] = pd.to_numeric(cruce_3["tarifa_fit"], errors="coerce")
    
    # Manejar columnas con sufijo doble
    tarifa_fsrr_col = "tarifa_fsrr_fsrr" if "tarifa_fsrr_fsrr" in cruce_3.columns else "tarifa_fsrr"
    provision_col = "provision_fsrr_fsrr" if "provision_fsrr_fsrr" in cruce_3.columns else "provision_fsrr"
    cruce_3["tarifa_fsrr"] = pd.to_numeric(cruce_3[tarifa_fsrr_col], errors="coerce")
    cruce_3["provision_fsrr"] = pd.to_numeric(cruce_3[provision_col], errors="coerce")
    cruce_3["diferencia_tarifa"] = cruce_3["tarifa_fit"] - cruce_3["tarifa_fsrr"]
    con_dif_3 = cruce_3[cruce_3["diferencia_tarifa"] != 0]
    sin_dif_3 = cruce_3[cruce_3["diferencia_tarifa"] == 0]
    
    # PASO 7C: Crear tabla FIT con APROBADO y MOTIVO
    df_resultado = df_fit.copy()
    df_resultado["APROBADO FIT"] = "SIN MATCH"
    df_resultado["MOTIVO"] = ""
    
    # Match intento 1
    guias_igual = set(sin_diferencia["guia"])
    guias_dif = set(con_diferencia["guia"])
    df_resultado.loc[df_resultado["guia"].isin(guias_igual), "APROBADO FIT"] = "APROBADO"
    df_resultado.loc[df_resultado["guia"].isin(guias_igual), "MOTIVO"] = "Match 4 llaves"
    df_resultado.loc[df_resultado["guia"].isin(guias_dif), "APROBADO FIT"] = "DIFERENCIA"
    df_resultado.loc[df_resultado["guia"].isin(guias_dif), "MOTIVO"] = "Tarifa diferente"
    
    # Match intento 2
    guias_match2 = set(cruce_2["guia"])
    guias_dif2 = set(con_dif_2["guia"]) if len(con_dif_2) > 0 else set()
    guias_ok2 = guias_match2 - guias_dif2
    df_resultado.loc[(df_resultado["APROBADO FIT"] == "SIN MATCH") & (df_resultado["guia"].isin(guias_ok2)), "APROBADO FIT"] = "APROBADO"
    df_resultado.loc[(df_resultado["APROBADO FIT"] == "APROBADO") & (df_resultado["guia"].isin(guias_ok2)), "MOTIVO"] = "Match sin fecha (fecha difiere)"
    df_resultado.loc[(df_resultado["APROBADO FIT"] == "SIN MATCH") & (df_resultado["guia"].isin(guias_dif2)), "APROBADO FIT"] = "DIFERENCIA"
    df_resultado.loc[(df_resultado["APROBADO FIT"] == "DIFERENCIA") & (df_resultado["guia"].isin(guias_dif2)) & (df_resultado["MOTIVO"] == ""), "MOTIVO"] = "Tarifa diferente + fecha difiere"
    
    # Match intento 3
    match3_ok = set(zip(sin_dif_3["fecha_guia"], sin_dif_3["distancia"], sin_dif_3["trafico"]))
    match3_dif = set(zip(con_dif_3["fecha_guia"], con_dif_3["distancia"], con_dif_3["trafico"]))
    df_resultado["_key3"] = list(zip(df_resultado["fecha_guia"], df_resultado["distancia"], df_resultado["trafico"]))
    mascara_sin_guia = (df_resultado["guia"] == "0") | (df_resultado["guia"] == "nan") | (df_resultado["guia"] == "")
    df_resultado.loc[mascara_sin_guia & df_resultado["_key3"].isin(match3_ok), "APROBADO FIT"] = "APROBADO"
    df_resultado.loc[mascara_sin_guia & df_resultado["_key3"].isin(match3_ok), "MOTIVO"] = "Match sin guía (fecha+tráfico+dist)"
    df_resultado.loc[mascara_sin_guia & df_resultado["_key3"].isin(match3_dif), "APROBADO FIT"] = "DIFERENCIA"
    df_resultado.loc[mascara_sin_guia & df_resultado["_key3"].isin(match3_dif), "MOTIVO"] = "Tarifa dif sin guía"
    df_resultado = df_resultado.drop(columns=["_key3"])
    
    # Locomotoras
    equipos_igual = set(sin_diferencia_loco["equipo"]) if len(sin_diferencia_loco) > 0 else set()
    equipos_dif = set(con_diferencia_loco["equipo"]) if len(con_diferencia_loco) > 0 else set()
    df_resultado.loc[(df_resultado["Clase"] == "LOCOMOTORA") & (df_resultado["equipo_fit"].isin(equipos_igual)), "APROBADO FIT"] = "APROBADO"
    df_resultado.loc[(df_resultado["Clase"] == "LOCOMOTORA") & (df_resultado["equipo_fit"].isin(equipos_igual)), "MOTIVO"] = "Match locomotora"
    df_resultado.loc[(df_resultado["Clase"] == "LOCOMOTORA") & (df_resultado["equipo_fit"].isin(equipos_dif)), "APROBADO FIT"] = "DIFERENCIA"
    df_resultado.loc[(df_resultado["Clase"] == "LOCOMOTORA") & (df_resultado["equipo_fit"].isin(equipos_dif)), "MOTIVO"] = "Tarifa diferente locomotora"
    
    # Sin match: motivos
    df_resultado.loc[(df_resultado["APROBADO FIT"] == "SIN MATCH") & (df_resultado["Clase"] == "LOCOMOTORA"), "MOTIVO"] = "Locomotora sin match en FSRR"
    df_resultado.loc[(df_resultado["APROBADO FIT"] == "SIN MATCH") & (df_resultado["Clase"] != "LOCOMOTORA"), "MOTIVO"] = "Guía no existe en FSRR"
    df_resultado.loc[
        (df_resultado["APROBADO FIT"] == "SIN MATCH") &
        (df_resultado["Clase"] != "LOCOMOTORA") &
        ((df_resultado["guia"] == "0") | (df_resultado["guia"] == "nan") | (df_resultado["guia"] == "")),
        "MOTIVO"] = "Sin número de guía"
    df_resultado.loc[
        (df_resultado["APROBADO FIT"] == "SIN MATCH") &
        (df_resultado["Clase"] != "LOCOMOTORA") &
        (df_resultado["MOTIVO"] == "Guía no existe en FSRR"),
        "MOTIVO"] = "Guía no encontrada en FSRR"
    
    # Retornar todo
    return {
        "df_fit": df_fit,
        "df_resultado": df_resultado,
        "coincidencias": coincidencias,
        "con_diferencia": con_diferencia,
        "sin_diferencia": sin_diferencia,
        "solo_fit_1": solo_fit_1,
        "solo_fsrr_1": solo_fsrr_1,
        "coincidencias_loco": coincidencias_loco,
        "con_diferencia_loco": con_diferencia_loco,
        "sin_diferencia_loco": sin_diferencia_loco,
        "solo_fit_loco": solo_fit_loco,
        "solo_fsrr_loco": solo_fsrr_loco,
        "cruce_2": cruce_2,
        "con_dif_2": con_dif_2,
        "sin_dif_2": sin_dif_2,
        "cruce_3": cruce_3,
        "con_dif_3": con_dif_3,
        "sin_dif_3": sin_dif_3,
        "dist_corregidas": dist_corregidas,
        "fechas_corregidas": fechas_corregidas,
    }

def generar_excel(datos, nombre, hojas):
    """Genera un archivo Excel en memoria"""
    output = BytesIO()
    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        for nombre_hoja, df in hojas.items():
            df.to_excel(writer, sheet_name=nombre_hoja, index=False)
    return output.getvalue()

# === APP PRINCIPAL ===
def app_principal():
    # Header
    col_header, col_logout = st.columns([5, 1])
    with col_header:
        st.markdown("""
        <div class="main-header">
            <h1>🚂 Derechos de Paso FIT - FSRR</h1>
            <p>Sistema de cruce y comparación de tarifas ferroviarias</p>
        </div>
        """, unsafe_allow_html=True)
    with col_logout:
        st.markdown("<br>", unsafe_allow_html=True)
        st.write(f"👤 **{st.session_state['usuario']}**")
        if st.button("Cerrar sesión", type="secondary"):
            cerrar_sesion()
    
    # Subir archivos
    st.markdown("### 📁 Cargar archivos")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        archivo_fit = st.file_uploader("**Archivo FIT** (hojas UDEA y LISTAS)", type=["xlsx", "xls"], key="fit")
    with col2:
        archivo_carros = st.file_uploader("**FSRR Carros**", type=["xlsx", "xls"], key="carros")
    with col3:
        archivo_loco = st.file_uploader("**FSRR Locomotoras**", type=["xlsx", "xls"], key="loco")
    
    # Procesar
    if archivo_fit and archivo_carros and archivo_loco:
        if st.button("🚀 Procesar cruce", type="primary", use_container_width=True):
            with st.spinner("Procesando datos... esto puede tardar unos segundos"):
                try:
                    r = procesar_datos(archivo_fit, archivo_carros, archivo_loco)
                    st.session_state["resultados"] = r
                    st.success("¡Procesamiento completado!")
                except Exception as e:
                    st.error(f"Error al procesar: {str(e)}")
                    return
    
    # Mostrar resultados
    if "resultados" in st.session_state:
        r = st.session_state["resultados"]
        
        st.markdown("---")
        st.markdown("### 📊 Resumen General")
        
        # Métricas principales
        aprobados = len(r["df_resultado"][r["df_resultado"]["APROBADO FIT"] == "APROBADO"])
        diferencias = len(r["df_resultado"][r["df_resultado"]["APROBADO FIT"] == "DIFERENCIA"])
        sin_match = len(r["df_resultado"][r["df_resultado"]["APROBADO FIT"] == "SIN MATCH"])
        total = len(r["df_resultado"])
        
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Total registros FIT</h3>
                <p class="number blue">{total:,}</p>
            </div>""", unsafe_allow_html=True)
        with c2:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Aprobados</h3>
                <p class="number green">{aprobados:,}</p>
            </div>""", unsafe_allow_html=True)
        with c3:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Diferencias</h3>
                <p class="number yellow">{diferencias:,}</p>
            </div>""", unsafe_allow_html=True)
        with c4:
            st.markdown(f"""
            <div class="metric-card">
                <h3>Sin match</h3>
                <p class="number red">{sin_match:,}</p>
            </div>""", unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Desglose carros vs locomotoras
        col_a, col_b = st.columns(2)
        
        with col_a:
            st.markdown("#### 🚃 FIT vs Carros")
            st.write(f"Coincidencias: **{len(r['coincidencias']):,}**")
            st.write(f"- Tarifa igual: {len(r['sin_diferencia']):,}")
            st.write(f"- Tarifa diferente: {len(r['con_diferencia']):,}")
            st.write(f"- Match 2do intento (sin fecha): {len(r['cruce_2']):,}")
            st.write(f"- Match 3er intento (sin guía): {len(r['cruce_3']):,}")
            if len(r['con_diferencia']) > 0:
                st.write(f"- **Monto diferencia: ${r['con_diferencia']['diferencia_tarifa'].sum():.2f}**")
        
        with col_b:
            st.markdown("#### 🚂 FIT vs Locomotoras")
            st.write(f"Coincidencias: **{len(r['coincidencias_loco']):,}**")
            st.write(f"- Tarifa igual: {len(r['sin_diferencia_loco']):,}")
            st.write(f"- Tarifa diferente: {len(r['con_diferencia_loco']):,}")
            if len(r['con_diferencia_loco']) > 0:
                st.write(f"- **Monto diferencia: ${r['con_diferencia_loco']['diferencia_tarifa'].sum():.2f}**")
        
        st.markdown("---")
        
        # Motivos
        st.markdown("#### 📋 Detalle por motivo")
        motivos = r["df_resultado"]["MOTIVO"].value_counts().reset_index()
        motivos.columns = ["Motivo", "Cantidad"]
        st.dataframe(motivos, use_container_width=True, hide_index=True)
        
        # Correcciones automáticas
        st.markdown("#### 🔧 Correcciones automáticas aplicadas")
        st.write(f"- Distancias corregidas: **{r['dist_corregidas']}**")
        st.write(f"- Fechas corregidas: **{r['fechas_corregidas']}**")
        st.write(f"- Estación estandarizada: *Ing A Lir Arciniega → Ing.A. Lira Arciniega*")
        
        st.markdown("---")
        
        # Descargas
        st.markdown("### 📥 Descargar resultados")
        
        c1, c2, c3, c4 = st.columns(4)
        
        with c1:
            excel_carros = generar_excel(r, "carros", {
                "Match": r["sin_diferencia"],
                "Diferencias": r["con_diferencia"],
                "Solo FIT": r["solo_fit_1"],
                "Solo FSRR": r["solo_fsrr_1"],
            })
            st.download_button(
                "📥 Cruce Carros", excel_carros,
                "CRUCE_CARROS.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )
        
        with c2:
            excel_loco = generar_excel(r, "loco", {
                "Match": r["sin_diferencia_loco"],
                "Diferencias": r["con_diferencia_loco"],
                "Solo FIT": r["solo_fit_loco"],
                "Solo FSRR": r["solo_fsrr_loco"],
            })
            st.download_button(
                "📥 Cruce Locomotoras", excel_loco,
                "CRUCE_LOCOMOTORAS.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )
        
        with c3:
            excel_adic = generar_excel(r, "adic", {
                "Match2 Sin Fecha": r["sin_dif_2"],
                "Dif2 Sin Fecha": r["con_dif_2"],
                "Match3 Sin Guia": r["sin_dif_3"],
                "Dif3 Sin Guia": r["con_dif_3"],
            })
            st.download_button(
                "📥 Cruces Adicionales", excel_adic,
                "CRUCE_ADICIONALES.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                width="stretch"
            )
        
        with c4:
            csv_resultado = r["df_resultado"].to_csv(index=False).encode("utf-8-sig")
            st.download_button(
                "📥 FIT Aprobado (CSV)", csv_resultado,
                "FIT_APROBADO.csv", "text/csv",
                width="stretch"
            )

# === EJECUCIÓN ===
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

if st.session_state["autenticado"]:
    app_principal()
else:
    login()
