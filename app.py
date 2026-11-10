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
# 4. የክልሎች እና የጉዞ መስመር ከዝርዝር ማቆሚያዎች ጋር (Detailed Route & Stops Tracker)
# ==========================================
st.markdown("---")
st.title("🗺️ የጉዞ መስመር፣ ሰፈሮች እና ማቆሚያዎች መቆጣጠሪያ")

# የኢትዮጵያ ዋና ዋና ሀይዌይ መስመሮች እና በመንገዱ ላይ የሚገኙ ትንንሽ ከተሞች/ሰፈሮች ከነ ኪሎሜትራቸው
edges_with_distance = [
    # ሀዋሳ መስመር
    ("አዲስ አበባ", "ቃሊቲ", 15),
    ("ቃሊቲ", "ቱሉ ዲምቱ", 10),
    ("ቱሉ ዲምቱ", "ደብረ ዘይት/ቢሾፍቱ", 20),
    ("ደብረ ዘይት/ቢሾፍቱ", "ሞጆ", 30),
    ("ሞጆ", "አዳማ", 25),
    ("ሞጆ", "መቂ", 50),
    ("መቂ", "ዝዋይ", 35),
    ("ዝዋይ", "አላባ", 60),
    ("አላባ", "ሻሸመኔ", 50),
    ("ሻሸመኔ", "ሀዋሳ", 25),
    ("ሀዋሳ", "አርצו", 40),
    ("አርצו", "ዲላ", 50),
    ("ዲላ", "አርባ ምንጭ", 130),
    
    # ጎጃም መስመር (ከአዲስ አበባ እስከ ባህር ዳር በዝርዝር)
    ("አዲስ አበባ", "ሱሉልታ", 25),
    ("ሱሉልታ", "ምარიም", 30),
    ("ምარიም", "ጎንደር በር/ፊንጫ", 40),
    ("ጎንደር በር/ፊንጫ", "ደብረ ማርቆስ", 205),
    ("ደብረ ማርቆስ", "አብረሃማ", 50),
    ("አብረሃማ", "ምስካይ", 60),
    ("ምስካይ", "ቢቸና መተሃ", 50),
    ("ቢቸና መተሃ", "ባህር ዳር", 100),
    ("ባህር ዳር", "አማኑኤል", 75),
    ("አማኑኤል", "ጎንደር", 100),

    # ደብረ ብርሃን - ደሴ - መቀሌ መስመር
    ("አዲስ አበባ", "ሰንዳፋ", 38),
    ("ሰንዳፋ", "ዐርባ ከርጠቻ", 30),
    ("ዐርባ ከርጠቻ", "ደብረ ብርሃን", 62),
    ("ደብረ ብርሃን", "አዲስ አለም", 45),
    ("አዲስ አለም", "ሸዋ ረቢ", 60),
    ("ሸዋ ረቢ", "ሚኤል", 70),
    ("ሚኤል", "ደሴ", 85),
    ("ደሴ", "ሐይቅ", 30),
    ("ሐይቅ", "ወልዲያ", 90),
    ("ወልዲያ", "አላማጣ", 70),
    ("አላማጣ", "መቀሌ", 130),
    ("መቀሌ", "አክሱም", 240),

    # ጅማ መስመር
    ("አዲስ አበባ", "ሰበታ", 25),
    ("ሰበታ", "እንጦጦ/ኢሉ", 35),
    ("እንጦጦ/ኢሉ", "አዲስ አለም (ጅማ መንገድ)", 30),
    ("አዲስ አለም (ጅማ መንገድ)", "አሶሳ መገናኛ", 60),
    ("አሶሳ መገናኛ", "ጅማ", 200),
    ("ጅማ", "ቦንጋ", 110),

    # አዋሽ - ድሬዳዋ - ሐረር መስመር
    ("አዳማ", "አዋሽ", 100),
    ("አዋሽ", "መተሀራ", 30),
    ("መተሀራ", "አዋሽ አርባ", 40),
    ("አዋሽ አርባ", "አይሰა", 50),
    ("አይሰა", "ጭሮ", 50),
    ("ጭሮ", "አሰበ ተፈሪ", 60),
    ("አሰበ ተፈሪ", "ድሬዳዋ", 70),
    ("ድሬዳዋ", "ሐረር", 55)
]

# Graph መፍጠር
G = nx.Graph()
for u, v, w in edges_with_distance:
    G.add_edge(u, v, weight=w)

all_cities = sorted(list(G.nodes()))

st.markdown("### 🛣️ የጉዞ ርቀት እና የሰፈሮች/ማቆሚያዎች ዝርዝር ማግኛ")
col_start, col_end = st.columns(2)
with col_start:
    start_point = st.selectbox("መነሻ ከተማ:", all_cities, index=all_cities.index("አዲስ አበባ") if "አዲስ አበባ" in all_cities else 0, key="start_route_det")
with col_end:
    end_point = st.selectbox("ድረሻ ከተማ:", all_cities, index=all_cities.index("ደብረ ማርቆስ") if "ደብረ ማርቆስ" in all_cities else min(1, len(all_cities)-1), key="end_route_det")

if st.button("ሁሉንም ሰፈሮች እና ርቀት ፈልግ (Find All Stops & Distance)"):
    try:
        path = nx.shortest_path(G, source=start_point, target=end_point, weight='weight')
        total_distance = nx.shortest_path_length(G, source=start_point, target=end_point, weight='weight')
        
        st.success(f"✅ ከ **{start_point}** እስከ **{end_point}** ያለው ጠቅላላ የጉዞ ርቀት: **ኮንትራት/ጠቅላላ {total_distance} ኪ.ሜ (Km)**")
        
        st.markdown("#### 📍 በመንገዱ ላይ የሚያልፉ ማቆሚያዎች፣ ሰፈሮች እና የክፍል ርቀቶች:")
        
        for i in range(len(path) - 1):
            u = path[i]
            v = path[i+1]
            dist = G[u][v]['weight']
            if i == 0:
                st.markdown(f"🟢 **1. መነሻ:** {u}")
            st.markdown(f"👉 ከ **{u}** ➔ **{v}** (የክፍል ርቀት: **{dist} ኪ.ሜ**)")
            if i == len(path) - 2:
                st.markdown(f"🏁 **መድረሻ:** {v}")
                
        st.info("➔ ".join(path))
        
    except nx.NetworkXNoPath:
        st.warning(f"⚠️ ከ '{start_point}' እስከ '{end_point}' ያለው ቀጥተኛ የመንገድ ትስስር አልተገኘም።")
