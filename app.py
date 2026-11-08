import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="የዕለት ስምሪት እና ሎጂስቲክስ አስተዳደር", page_icon="🚚")

st.title("🚚 የዕለት ስምሪት እና ሎጂስቲክስ ክትትል ሲስተም")
st.markdown("---")

EXCEL_FILE = "Dispatch_Management_Form.xlsx"

@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            df = pd.read_excel(EXCEL_FILE)
            df = df.dropna(subset=['Order No / የትዕዛዝ ቁጥር'])
            return df
        except Exception as e:
            st.error(f"ስህተት ተፈጥሯል: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

if not df.empty:
    col1, col2, col3, col4 = st.columns(4)
    
    total_orders = len(df)
    company_count = len(df[df['Fleet Ownership / የመኪና ባለቤትነት'] == 'Company'])
    hired_count = len(df[df['Fleet Ownership / የመኪና ባለቤትነት'] == 'Hired/የኪራይ'])
    total_cost = df['Freight Cost / የትራንስፖርት ወጪ'].sum()

    col1.metric("ጠቅላላ ትዕዛዞች", f"{total_orders}")
    col2.metric("የድርጅት መኪና ብዛት", f"{company_count}")
    col3.metric("የኪራይ መኪና ብዛት", f"{hired_count}")
    col4.metric("ጠቅላላ የትራንስፖርት ወጪ", f"{total_cost:,.2f} ETB")

    st.markdown("### 📋 የዕለት ትዕዛዞች እና ስምሪት ዝርዝር")
    st.dataframe(df, use_container_width=True)

    st.markdown("### 📊 በአቅጣጫ የተከፋፈለ ጭነት (Weight by Route)")
    if 'Route / አቅጣጫ' in df.columns and 'Cargo Weight (Kg/Ton)' in df.columns:
        route_summary = df.groupby('Route / አቅጣጫ')['Cargo Weight (Kg/Ton)'].sum()
        st.bar_chart(route_summary)
else:
    st.warning(f"እባክዎ '{EXCEL_FILE}' የተባለው ፋይል ሪፖዚተሪዎ ውስጥ መኖሩን ይዩ!")
