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
# 4. የክልሎች እና የጉዞ መስመር ከኪሎሜተር ስሌት ጋር (Route & Distance Tracker)
# ==========================================
st.markdown("---")
st.title("🗺️ የጉዞ መስመር፣ ማቆሚያዎች እና የርቀት (Km) መቆጣጠሪያ")

# በከተሞች መካከል ያሉ ግምታዊ ርቀቶች (በኪ.ሜ) የተካተቱበት መረብ
edges_with_distance = [
    ("አዲስ አበባ", "ቢሾፍቱ", 45),
    ("ቢሾፍቱ", "ሞጆ", 30),
    ("ሞጆ", "አዳማ", 25),
    ("ሞጆ", "መቂ", 50),
    ("መቂ", "ዝዋይ", 35),
    ("ዝዋይ", "ሻሸመኔ", 110),
    ("ሻሸመኔ", "ሀዋሳ", 25),
    ("ሀዋሳ", "ዲላ", 90),
    ("ዲላ", "አርባ ምንጭ", 130),
    
    ("አዲስ አበባ", "ሰንዳፋ", 38),
    ("ሰንዳፋ", "ደብረ ብርሃን", 92),
    ("ደብረ ብርሃን", "ደሴ", 260),
    ("ደሴ", "ሰመራ", 265),
    ("ደሴ", "ወልዲያ", 120),
    ("ወልዲያ", "መቀሌ", 200),
    ("መቀሌ", "አክሱም", 240),

    ("አዲስ አበባ", "ደብረ ማርቆስ", 300),
    ("ደብረ ማርቆስ", "ባህር ዳር", 260),
    ("ባህር ዳር", "ጎንደር", 175),

    ("አዲስ አበባ", "ጅማ", 350),
    ("ጅማ", "ቦንጋ", 110),

    ("አዳማ", "አዋሽ", 100),
    ("አዋሽ", "መተሀራ", 30),
    ("መተሀራ", "ጭሮ", 140),
    ("ጭሮ", "ድሬዳዋ", 130),
    ("ድሬዳዋ", "ሐረር", 55)
]

# Graph መፍጠር እና ርቀቶችን (weight) መጫን
G = nx.Graph()
for u, v, w in edges_with_distance:
    G.add_edge(u, v, weight=w)

all_cities = sorted(list(G.nodes()))

st.markdown("### 🛣️ የጉዞ ርቀት እና ማቆሚያዎች ማግኛ")
col_start, col_end = st.columns(2)
with col_start:
    start_point = st.selectbox("መነሻ ከተማ:", all_cities, index=all_cities.index("አዲስ አበባ") if "አዲስ አበባ" in all_cities else 0, key="start_route_km")
with col_end:
    end_point = st.selectbox("ድረሻ ከተማ:", all_cities, index=all_cities.index("ሀዋሳ") if "ሀዋሳ" in all_cities else min(1, len(all_cities)-1), key="end_route_km")

if st.button("ርቀቱን እና ሙሉውን መስመር ፈልግ (Calculate Route & Distance)"):
    try:
        # አጭር መንገድ እና ጠቅላላ ርቀት ማሰላት
        path = nx.shortest_path(G, source=start_point, target=end_point, weight='weight')
        total_distance = nx.shortest_path_length(G, source=start_point, target=end_point, weight='weight')
        
        st.success(f"✅ ከ **{start_point}** እስከ **{end_point}** ያለው ጠቅላላ የጉዞ ርቀት: **{total_distance} ኪ.ሜ (Km)**")
        
        st.markdown("#### 📍 የደረጃ በደረጃ ማቆሚያዎች እና የክፍል ርቀቶች:")
        
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            dist = G[u][v]['weight']
            if i == 0:
                st.markdown(f"🟢 **1. መነሻ:** {u}")
            st.markdown(f"👉 ከ **{u}** ወደ **{v}** ➔ **{dist} ኪ.ሜ**")
            if i == len(path) - 2:
                st.markdown(f"🏁 **መድረሻ:** {v}")
                
        st.info("ፋና ➔ " + " ➔ ".join(path))
        
    except nx.NetworkXNoPath:
        st.warning(f"⚠️ ከ '{start_point}' እስከ '{end_point}' ያለው ቀጥተኛ የመንገድ ትስስር አልተገኘም።")
    
