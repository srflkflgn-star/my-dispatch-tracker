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
# 4. የድርጅት ሎኬሽን (AMG Holdings Gelan) እና የጉዞ መስመር መቆጣጠሪያ
# ==========================================
st.markdown("---")
st.title("🏢 የድርጅት ሎኬሽን (AMG Holdings - Gelan) እና የጉዞ መስመር መቆጣጠሪያ")

st.markdown("### 📍 የድርጅቱ መገኛ (AMG Holdings Industry Park - Gelan)")
st.markdown("የድርጅቱ ማዕከል/ፋብሪካ የሚገኘው በ **ገላን (Gelan)** ይገኛል[cite: 1, 3]። ከዚህ በታች ካለው ሊንክ በቀጥታ በ Google Maps ማየት ይችላሉ፡")
st.markdown("[🗺️ የ AMG Holdings Gelan ሎኬሽን በ Google Maps ለመክፈት እዚህ ይጫኑ](https://www.google.com/maps/place//data=!4m2!3m1!19sChIJKQJqLAB5SxYR0u9ih_8JK5Q)")

edges_with_distance = [
    # የአዲስ አበባ ሰፈሮች እርስ በእርስ እና ወደ ገላን ማገናኛ መንገዶች
    ("አዲስ አበባ - ፒያሳ", "አዲስ አበባ - አራት ኪሎ", 3),
    ("አዲስ አበባ - አራት ኪሎ", "አዲስ አበባ - መገናኛ", 7),
    ("አዲስ አበባ - ፒያሳ", "አዲስ አበባ - መርካቶ", 4),
    ("አዲስ አበባ - መርካቶ", "አዲስ አበባ - አስኮ", 6),
    ("አዲስ አበባ - ፒያሳ", "አዲስ አበባ - ቦሌ", 8),
    ("አዲስ አበባ - ቦሌ", "አዲስ አበባ - መገናኛ", 4),
    ("አዲስ አበባ - ቦሌ", "አዲስ አበባ - ሳሪስ", 8),
    ("አዲስ አበባ - ሳሪስ", "አዲስ አበባ - ቃሊቲ", 5),
    
    # ከቃሊቲ/ሳሪስ ወደ AMG Holdings Gelan የሚወስድ መስመር
    ("አዲስ አበባ - ቃሊቲ", "ቱሉ ዲምቱ", 10),
    ("ቱሉ ዲምቱ", "ደብረ ዘይት/ቢሾፍቱ", 20),
    ("ደብረ ዘይት/ቢሾፍቱ", "ሞጆ", 30),
    ("ሞጆ", "AMG Holdings - Gelan", 15),

    # ከገላን እና ከሞጆ በመቂ መካከል ያሉ ተጨማሪ ዝርዝር ማቆሚያዎች (ሰፈሮች)
    ("AMG Holdings - Gelan", "አዳማ", 45),
    ("AMG Holdings - Gelan", "ሞጆ", 15),
    
    # **በሞጆ እና መቂ መካከል ያሉ ትንንሽ ማቆሚያዎች/ሰፈሮች**
    ("ሞጆ", "አቃቂ ኬላ (ሞጆ)", 10),
    ("አቃቂ ኬላ (ሞጆ)", "ዶዶላ መገናኛ", 15),
    ("ዶዶላ መገናኛ", "መቂ", 25),

    ("መቂ", "Kella/መቂ ኬላ", 15),
    ("Kella/መቂ ኬላ", "ዝዋይ", 20),
    ("ዝዋይ", "አላባ", 60),
    ("አላባ", "ሻሸመኔ", 50),
    ("ሻሸመኔ", "ሀዋሳ", 25),
    ("ሀዋሳ", "ዲላ", 90),

    # ሌሎች መስመሮች
    ("አዳማ", "አዋሽ", 100),
    ("አዋሽ", "መተሀራ", 30),
    ("መተሀራ", "ድሬዳዋ", 170),
    ("ድሬዳዋ", "ሐረር", 55),
    
    ("አዲስ አበባ - መርካቶ", "አዲስ አበባ - አስኮ", 6),
    ("አዲስ አበባ - አስኮ", "ሱሉልታ", 15),
    ("ሱሉልታ", "ደብረ ማርቆስ", 245),
    ("ደብረ ማርቆስ", "ባህር ዳር", 260)
]

G = nx.Graph()
for u, v, w in edges_with_distance:
    G.add_edge(u, v, weight=w)

all_locations = sorted(list(G.nodes()))

st.markdown("### 🛣️ ከየትኛውም ሰፈር ወይም ከተማ እስከ መድረሻ ያለው ርቀት እና የሰፈሮች ዝርዝር ማግኛ")
col_start, col_end = st.columns(2)
with col_start:
    start_point = st.selectbox("መነሻ (ሰፈር ወይም ከተማ):", all_locations, index=0, key="start_route_amg_det")
with col_end:
    default_end_idx = all_locations.index("መቂ") if "መቂ" in all_locations else min(1, len(all_locations)-1)
    end_point = st.selectbox("ድረሻ (መድረሻ ሎኬሽን):", all_locations, index=default_end_idx, key="end_route_amg_det")

if st.button("መንገዱን፣ ሰፈሮቹን እና ርቀት ፈልግ"):
    try:
        path = nx.shortest_path(G, source=start_point, target=end_point, weight='weight')
        total_distance = nx.shortest_path_length(G, source=start_point, target=end_point, weight='weight')
        
        st.success(f"✅ ከ **{start_point}** እስከ **{end_point}** ያለው ጠቅላላ ርቀት: **{total_distance} ኪ.ሜ (Km)**")
        
        st.markdown("#### 📍 በመንገዱ ላይ የሚያልፉ ሰፈሮች፣ ማቆሚያዎች እና የክፍል ርቀቶች:")
        
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
