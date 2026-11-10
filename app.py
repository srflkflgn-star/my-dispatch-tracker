import streamlit as st
import pandas as pd
import os
import networkx as nx

st.set_page_config(page_title="የዕለት ስምሪት እና ሎጂስቲክስ አስተዳደር", page_icon="🚚", layout="wide")

st.title("🚚 የዕለት ስምሪት እና ሎጂስቲክስ ክትትል ሲስተም")
st.markdown("---")

EXCEL_FILE = "Dispatch_Management_Form.xlsx"

@st.cache_data
def load_data():
    if os.path.exists(EXCEL_FILE):
        try:
            # ርዕሶቹ ያሉት በ 3ተኛው ረድፍ (header=2) ላይ መሆኑን ማረጋገጥ
            df = pd.read_excel(EXCEL_FILE, engine='openpyxl', header=2)
            if 'Order No / የትዕዛዝ ቁጥር' in df.columns:
                df = df.dropna(subset=['Order No / የትዕዛዝ ቁጥር'])
            return df
        except Exception as e:
            st.error(f"ስህተት ተፈጥሯል: {e}")
            return pd.DataFrame()
    return pd.DataFrame()

df = load_data()

if not df.empty:
    df.columns = df.columns.str.strip()

    # 1. ኪፒአይ ማጠቃለያዎች (KPI Metrics)
    col1, col2, col3, col4 = st.columns(4)
    
    total_orders = len(df)
    company_count = 0
    hired_count = 0
    ownership_col = 'Fleet Ownership / የመኪና ባለቤትነት'
    
    if ownership_col in df.columns:
        company_count = len(df[df[ownership_col].astype(str).str.contains('Company', case=False, na=False)])
        hired_count = len(df[df[ownership_col].astype(str).str.contains('Hired|የኪራይ', case=False, na=False)])

    total_cost = 0.0
    cost_col = 'Freight Cost / የትራንስፖርት ወጪ'
    if cost_col in df.columns:
        total_cost = pd.to_numeric(df[cost_col], errors='coerce').sum()

    col1.metric("ጠቅላላ ትዕዛዞች", f"{total_orders}")
    col2.metric("የድርጅት መኪና", f"{company_count}")
    col3.metric("የኪራይ መኪና", f"{hired_count}")
    col4.metric("ጠቅላላ ወጪ", f"{total_cost:,.2f} ETB")

    st.markdown("---")

    # 2. የዕለት ትዕዛዞች ሰንጠረዥ
    st.markdown("### 📋 የዕለት ትዕዛዞች እና ስምሪት ዝርዝር")
    st.dataframe(df, use_container_width=True)

    # 3. ግራፍ ማሳያ
    st.markdown("### 📊 በአቅጣጫ የተከፋፈለ ጭነት (Weight by Route)")
    route_col = 'Route / አቅጣጫ'
    weight_col = 'Cargo Weight (Kg/Ton)'
    
    if route_col in df.columns and weight_col in df.columns:
        df[weight_col] = pd.to_numeric(df[weight_col], errors='coerce')
        route_summary = df.groupby(route_col)[weight_col].sum()
        st.bar_chart(route_summary)
else:
    st.warning(f"እባክዎ '{EXCEL_FILE}' ፋይል ውስጥ ትክክለኛ መረጃ መኖሩን ይዩ!")

# ==========================================
# 4. የክልሎች እና የጉዞ መስመር መመሪያ (Route Tracker)
# ==========================================
st.markdown("---")
st.title("🗺️ የክልሎች እና የጉዞ መስመር (Route Tracker) መመሪያ")

routes_data = {
    "አዲስ አበባ": ["አዳማ", "ባህር ዳር", "ሀዋሳ", "ጅማ", "ደሴ"],
    "አዳማ": ["አዲስ አበባ", "ሰመራ", "ሐረር", "አዋሽ"],
    "ባህር ዳር": ["አዲስ አበባ", "ጎንደር", "ደብረ ማርቆስ"],
    "ሀዋሳ": ["አዲስ አበባ", "ዲላ", "አርባ ምንጭ"],
    "ደሴ": ["አዲስ አበባ", "መቀሌ", "ሰመራ"],
    "ሐረር": ["አዳማ", "ድሬዳዋ"],
    "ድሬዳዋ": ["ሐረር", "አዋሽ"],
    "መቀሌ": ["ደሴ", "አክሱም"],
    "ጅማ": ["አዲስ አበባ", "ቤንች ማጂ"],
    "አርባ ምንጭ": ["ሀዋሳ", "አስታማሚ ከተሞች"]
}

G = nx.Graph()
for city, neighbors in routes_data.items():
    for neighbor in neighbors:
        G.add_edge(city, neighbor)

selected_city = st.selectbox("የሚፈልጉትን ከተማ/ክልል ይምረጡ ወይም ይጻፉ:", list(routes_data.keys()))

if selected_city:
    st.markdown(f"### 📍 ስለ **{selected_city}** የተገኙ መረጃዎች፡")
    connected_destinations = routes_data.get(selected_city, [])
    
    col_a, col_b = st.columns(2)
    
    with col_a:
        st.info("🔄 ቀጥተኛ መውጫ መስመሮች (Next Destinations):")
        for dest in connected_destinations:
            st.write(f"👉 **{dest}**")
            
    with col_b:
        st.success("⬅️ የሚቀድሙት/መነሻ ሊሆኑ የሚችሉ:")
        predecessors = [city for city, targets in routes_data.items() if selected_city in targets]
        for pred in predecessors:
            st.write(f"👈 **{pred}**")

    st.markdown("---")
    st.subheader("🛣️ የሁለት መዳረሻዎች አጭር መንገድ ማግኛ")
    dest_options = list(routes_data.keys())
    start_point = st.selectbox("መነሻ ከተማ:", dest_options, index=0, key="start_route")
    end_point = st.selectbox("ድረሻ ከተማ:", dest_options, index=min(1, len(dest_options)-1), key="end_route")
    
    if st.button("መስመር ፈልግ (Find Route)"):
        try:
            path = nx.shortest_path(G, source=start_point, target=end_point)
            st.success(f"✅ ትክክለኛው የጉዞ ቅደም ተከተል: {' ➔ '.join(path)}")
        except nx.NetworkXNoPath:
            st.warning("⚠️ በእነዚህ ከተሞች መካከል ቀጥተኛ የተያያዘ መስመር አልተገኘም።")
