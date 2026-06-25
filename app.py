import streamlit as st
import pandas as pd
import io

# Professionelles Seiten-Setup mit Dark/Light-adaptiver Konfiguration
st.set_page_config(
    page_title="Risk Analytics Dashboard", 
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS für ein hochwertiges Enterprise-Design
st.markdown("""
    <style>
        .main .block-container { padding-top: 2rem; }
        .stAlert { border-radius: 8px; }
        h1, h2, h3 { font-weight: 700 !important; }
        .stMetric { background-color: rgba(28, 131, 225, 0.05); padding: 15px; border-radius: 10px; border: 1px solid rgba(28, 131, 225, 0.1); }
    </style>
""", unsafe_allow_html=True)

st.title("📊 Risk Analytics Dashboard")
st.caption("Professionelles Werkzeug zur Risikoanalyse und Korrelationsprüfung")
st.markdown("---")

# =========================
# SIDEBAR / SELECTION
# =========================
with st.sidebar:
    st.header("⚙️ Einstellungen")
    
    # Flexibler Input für den Tabellennamen (Standard: Tabelle1)
    sheet_input = st.text_input(
        "Excel-Tabellenblatt Name", 
        value="Tabelle1", 
        help="Gib hier den Namen des Tabellenblatts ein (z.B. Tabelle1, Tabelle3, etc.)"
    )
    
    st.markdown("---")
    uploaded_file = st.file_uploader("📂 Excel Datei hochladen", type=["xlsx"])

df = None
corr = None

if uploaded_file is not None:
    try:
        # Laden des dynamisch gewählten Tabellenblatts
        df = pd.read_excel(
            uploaded_file,
            sheet_name=sheet_input,
            index_col=0
        )

        df.index = pd.to_datetime(df.index, errors="coerce")
        df = df.apply(pd.to_numeric, errors="coerce")
        corr = df.corr()

    except ValueError:
        st.sidebar.error(f"❌ Das Blatt '{sheet_input}' wurde in der Datei nicht gefunden.")
    except Exception as e:
        st.sidebar.error(f"❌ Fehler beim Laden: {e}")

# =========================
# MAIN LAYOUT (3 SPALTEN)
# =========================
left, middle, right = st.columns([2, 2, 2], gap="large")

# =========================
# LINKS: DATENBASIS
# =========================
with left:
    st.subheader("📋 Rohdaten")
    
    if df is not None:
        st.dataframe(
            df, 
            use_container_width=True, 
            height=450
        )
    else:
        st.info("Bitte lade eine Excel-Datei in der Seitenleiste hoch.")

# =========================
# MITTE: KORRELATIONSMATRIX
# =========================
with middle:
    st.subheader("🔍 Korrelationsanalyse")

    if corr is not None:
        st.markdown(f"**Koeffizienten-Matrix ({sheet_input})**")
        try:
            st.dataframe(
                corr.style.background_gradient(cmap="coolwarm", axis=None).format(precision=3),
                use_container_width=True,
                height=450
            )
        except Exception:
            st.dataframe(
                corr.round(3),
                use_container_width=True,
                height=450
            )
    else:
        st.info("Warte auf Daten für die Korrelationsmatrix...")

# =========================
# RECHTS: METRIKEN & DOWNLOAD
# =========================
with right:
    st.subheader("⚡ Ergebnisse & Export")
    
    if df is not None and corr is not None:
        # Metriken in übersichtlichen Containern
        m1, m2 = st.columns(2)
        with m1:
            st.metric("Zeilen", len(df))
        with m2:
            st.metric("Spalten", len(df.columns))
            
        st.metric("Fehlende Werte (NaN)", int(df.isna().sum().sum()))
        
        st.markdown("### 🚨 Risiko-Regeln (Schwellenwert >= 0.8)")
        threshold = 0.8
        risks = []

        for i in corr.columns:
            for j in corr.columns:
                if i != j and corr.columns.get_loc(i) < corr.columns.get_loc(j): # Dubletten verhindern
                    val = corr.loc[i, j]
                    if abs(val) >= threshold:
                        risks.append(f"**{i}** ↔ **{j}** = `{val:.3f}`")

        if risks:
            for r in risks:
                st.warning(r)
        else:
            st.success("Optimal: Keine kritischen Korrelationen identifiziert.")
            
        st.markdown("---")
        st.markdown("### 📥 Daten sichern")
        
        # Professioneller Excel-Export im Hintergrund
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
            corr.to_excel(writer, sheet_name=f"Korrelation_{sheet_input}")
        
        st.download_button(
            label="📈 Korrelationen als Excel exportieren",
            data=buffer.getvalue(),
            file_name=f"korrelationskoeffizienten_{sheet_input}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    else:
        st.info("Lade Daten hoch, um Metriken und Export freizuschalten.")
