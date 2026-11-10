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
# 4. የክልሎች እና የጉዞ መስመር መመሪያ (Route Tracker with Intermediate Towns)
# ==========================================
st.markdown("---")
st.title("🗺️ የጉዞ መስመር እና መካከለኛ ከተሞች ማግኛ (Route & Stops Tracker)")

# የኢትዮጵያ ዋና ዋና ሀይዌይ መስመሮች እና በመንገዱ ላይ የሚገኙ ከተሞች ትስስር
routes_data = {
    # የሀዋሳ መስመር (Addis - Hawassa Corridor)
    "አዲስ አበባ": ["ቢሾፍቱ", "አዳማ", "ደብረ ብርሃን", "ደብረ ማርቆስ", "ጅማ"],
    "ቢሾፍቱ": ["አዲስ አበባ", "ሞጆ"],
    "ሞጆ": ["ቢሾፍቱ", "አዳማ", "መቂ"],
    "አዳማ": ["አዲስ አበባ", "ሞጆ", "አዋሽ"],
    "መቂ": ["ሞጆ", "ዝዋይ"],
    "ዝዋይ": ["መቂ", "ሻሸመኔ"],
    "ሻሸመኔ": ["ዝዋይ", "ሀዋሳ"],
    "ሀዋሳ": ["ሻሸመኔ", "ዲላ"],
    "ዲላ": ["ሀዋሳ", "አርባ ምንጭ"],
    "አርባ ምንጭ": ["ዲላ"],
    
    # የሰሜን መስመር (Dessie & Mekelle Corridor)
    "ደብረ ብርሃን": ["አዲስ አበባ", "ሰንዳፋ", "ደሴ"],
    "ሰንዳፋ": ["አዲስ አበባ", "ደብረ ብርሃን"],
    "ደሴ": ["ደብረ ብርሃን", "ወልዲያ", "ሰመራ"],
    "ወልዲያ": ["ደሴ", "መቀሌ"],
    "መቀሌ": ["ወልዲያ", "አክሱም"],
    "አክሱም": ["መቀሌ"],

    # የባህር ዳር መስመር (Bahir Dar & Gondar Corridor)
    "ደብረ ማርቆስ": ["አዲስ አበባ", "ባህር ዳር"],
    "ባህር ዳር": ["ደብረ ማርቆስ", "ጎንደር"],
    "ጎንደር": ["ባህር ዳር"],

    # የጅማ መስመር (Jimma Corridor)
    "ጅማ": ["አዲስ አበባ", "ቦንጋ"],
    "ቦንጋ": ["ጅማ"],

    # የምስራቅ መስመር (Awash - Dire Dawa - Harar Corridor)
    "አዋሽ": ["አዳማ", "መተሀራ"],
    "መተሀራ": ["አዋሽ", "ጭሮ"],
    "ጭሮ": ["መተሀራ", "ድሬዳዋ"],
    "ድሬዳዋ": ["ጭሮ", "ሐረር"],
    "ሐረር": ["ድሬዳዋ"],
    "ሰመራ": ["ደሴ"]
}

G = nx.Graph()
for city, neighbors in routes_data.items():
    for neighbor in neighbors:
        G.add_edge(city, neighbor)

# ሁሉንም ከተሞች በዝርዝር ለማስቀመጥ
all_cities = sorted(list(routes_data.keys()))

st.markdown("### 🛣️ የሁለት መዳረሻዎች ሙሉ የጉዞ መስመር እና ማቆሚያዎች")
col_start, col_end = st.columns(2)
with col_start:
    start_point = st.selectbox("መነሻ ከተማ:", all_cities, index=all_cities.index("አዲስ አበባ") if "አዲስ አበባ" in all_cities else 0, key="start_route")
with col_end:
    end_point = st.selectbox("ድረሻ ከተማ:", all_cities, index=all_cities.index("ሀዋሳ") if "ሀዋሳ" in all_cities else min(1, len(all_cities)-1), key="end_route")

if st.button("ሙሉውን የመንገድ ቅደም ተከተል ፈልግ (Find Full Route)"):
    try:
        # አጫጭሩን መንገድ ከመካከለኛ ከተሞች ጋር ማግኘት
        path = nx.shortest_path(G, source=start_point, target=end_point)
        
        st.success(f"✅ ከ **{start_point}** እስከ **{end_point}** ያለው ትክክለኛው የጉዞ ቅደም ተከተል እና ማቆሚያዎች:")
        
        # መንገዱን በደረጃ በደረጃ ማሳየት
        for i, stop in enumerate(path, 1):
            if i == 1:
                st.markdown(f"🟢 **{i}. መነሻ:** {stop}")
            elif i == len(path):
                st.markdown(f"🏁 **{i}. መድረሻ:** {stop}")
            else:
                st.markdown(f"📍 **{i}. ማቆሚያ / የሚያልፍበት ከተማ:** {stop}")
                
        # በእይታ እንዲመች በቀስት ማሳየት
        st.info("➔ ".join(path))
        
    except nx.NetworkXNoPath:
        st.warning(f"⚠️ ከ '{start_point}' እስከ '{end_point}' ያለው ቀጥተኛ የመንገድ ትስስር በዚህ ዝርዝር ውስጥ አልተገኘም።")
