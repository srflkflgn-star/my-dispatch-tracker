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
# 4. የኢትዮጵያ አጠቃላይ የጉዞ መስመር እና የርቀት መቆጣጠሪያ (Comprehensive Road Network)
# ==========================================
st.markdown("---")
st.title("🏢 የድርጅት ሎኬሽን (AMG Holdings - Gelan) እና አጠቃላይ የኢትዮጵያ የጉዞ መስመር")

st.markdown("### 📍 የድርጅቱ መገኛ (AMG Holdings Industry Park - Gelan)")
st.markdown("የድርጅቱ ማዕከል/ፋብሪካ የሚገኘው በ **ገላን (Gelan)** ይገኛል። ከዚህ በታች ካለው ሊንክ በቀጥታ በ Google Maps ማየት ይችላሉ፡")
st.markdown("[🗺️ የ AMG Holdings Gelan ሎኬሽን በ Google Maps ለመክፈት እዚህ ይጫኑ](https://www.google.com/maps/place//data=!4m2!3m1!19sChIJKQJqLAB5SxYR0u9ih_8JK5Q)")

edges_with_distance = [
    # --- 1. የአዲስ አበባ ሰፈሮች እና የኢንዱስትሪ ዞኖች ትስስር ---
    ("አዲስ አበባ - ፒያሳ", "አዲስ አበባ - አራት ኪሎ", 3),
    ("አዲስ አበባ - አራት ኪሎ", "አዲስ አበባ - መገናኛ", 7),
    ("አዲስ አበባ - ፒያሳ", "አዲስ አበባ - መርካቶ", 4),
    ("አዲስ አበባ - መርካቶ", "አዲስ አበባ - አስኮ", 6),
    ("አዲስ አበባ - ፒያሳ", "አዲስ አበባ - ቦሌ", 8),
    ("አዲስ አበባ - ቦሌ", "አዲስ አበባ - ሳሪስ", 8),
    ("አዲስ አበባ - ሳሪስ", "አዲስ አበባ - ቃሊቲ", 5),
    ("አዲስ አበባ - ቃሊቲ", "ቱሉ ዲምቱ", 10),
    ("ቱሉ ዲምቱ", "AMG Holdings - Gelan", 12),

    # --- 2. የደቡብ / ሀዋሳ / ሞያሌ ኮሪደር (Southern Corridor) ---
    ("AMG Holdings - Gelan", "ቢሾፍቱ (ደብረ ዘይት)", 20),
    ("ቢሾፍቱ (ደብረ ዘይት)", "ሞጆ", 30),
    ("ሞጆ", "አዳማ", 25),
    ("ሞጆ", "መቂ", 50),
    ("መቂ", "ዝዋይ (ቱሉ አብረሃ)", 35),
    ("ዝዋይ (ቱሉ አብረሃ)", "አላባ", 60),
    ("አላባ", "ሻሸመኔ", 50),
    ("ሻሸመኔ", "ሀዋሳ", 25),
    ("ሀዋሳ", "አርצו", 40),
    ("አርצו", "ዲላ", 50),
    ("ዲላ", "ወላይታ ሶዶ መገናኛ", 70),
    ("ወላይታ ሶዶ መገናኛ", "አርባ ምንጭ", 90),
    ("አርባ ምንጭ", "ሀመር / አስታማሚ", 120),
    ("ሀመር / አስታማሚ", "ሞያሌ (የኢትዮ-ኬንያ ድንበር)", 250),

    # --- 3. የምስራቅ / አዋሽ / ድሬዳዋ / ሐረር / ጅጅጋ ኮሪደር (Eastern Corridor) ---
    ("አዳማ", "አዋሽ", 100),
    ("አዋሽ", "መተሀራ", 30),
    ("መተሀራ", "አዋሽ አርባ", 40),
    ("አዋሽ አርባ", "አይሰა", 50),
    ("አይሰა", "ጭሮ (አሰበ ተፈሪ)", 90),
    ("ጭሮ (አሰበ ተፈሪ)", "ሐረማያ", 110),
    ("ሐረማያ", "ድሬዳዋ", 60),
    ("ድሬዳዋ", "ሐረር", 55),
    ("ሐረር", "ባቢሌ", 50),
    ("ባቢሌ", "ጅጅጋ", 100),

    # --- 4. ሰሜን / ጎጃም ኮሪደር (Northern - Gojam Corridor) ---
    ("አዲስ አበባ - አስኮ", "ሙግር መገናኛ", 10),
    ("ሙግር መገናኛ", "ሱሉልታ", 15),
    ("ሱሉልታ", "ማርያም (ሱሉልታ አከባቢ)", 25),
    ("ማርያም (ሱሉልታ አከባቢ)", "ፍቼ መገናኛ (ጣይታ)", 35),
    ("ፍቼ መገናኛ (ጣይታ)", "ሙርጃ / ደርባ", 40),
    ("ሙርጃ / ደርባ", "ጎንደር በር", 95),
    ("ጎንደር በር", "ደብረ ማርቆስ", 50),
    ("ደብረ ማርቆስ", "አብረሃማ", 50),
    ("አብረሃማ", "ምስካይ", 60),
    ("ምስካይ", "ቢቸና", 50),
    ("ቢቸና", "ባህር ዳር", 100),
    ("ባህር ዳር", "አማኑኤል", 75),
    ("አማኑኤል", "አዲስ ዘመን", 80),
    ("አዲስ ዘመን", "ጎንደር", 95),
    ("ጎንደር", "አክሱም", 240),
    ("አክሱም", "አድዋ", 35),
    ("አድዋ", "መቀሌ", 200),

    # --- 5. የሰሜን-ምስራቅ / ደብረ ብርሃን / ደሴ / መቀሌ ኮሪደር (Dessie - Mekelle Corridor) ---
    ("አዲስ አበባ - መገናኛ", "አዲስ አበባ - ለገጣፎ", 10),
    ("አዲስ አበባ - ለገጣፎ", "ሰንዳፋ", 28),
    ("ሰንዳፋ", "ዐርባ ከርጠቻ", 30),
    ("ዐርባ ከርጠቻ", "ደብረ ብርሃን", 62),
    ("ደብረ ብርሃን", "አዲስ አለም", 45),
    ("አዲስ አለም", "ሸዋ ረቢ", 60),
    ("ሸዋ ረቢ", "ሚኤል", 70),
    ("ሚኤል", "ደሴ", 85),
    ("ደሴ", "ሐይቅ", 30),
    ("ሐይቅ", "ወልዲያ", 90),
    ("ወልዲያ", "ሰመራ", 220),
    ("ወልዲያ", "አላማጣ", 70),
    ("አላማጣ", "መቀሌ", 130),

    # --- 6. ምዕራብ / ጅማ / ቤንች ማጂ / ጋምቤላ ኮሪደር (Western Corridor) ---
    ("አዲስ አበባ - መርካቶ", "ሰበታ", 22),
    ("ሰበታ", "እንጦጦ/ኢሉ", 35),
    ("እንጦጦ/ኢሉ", "አዲስ አለም (ጅማ መንገድ)", 30),
    ("አዲስ አለም (ጅማ መንገድ)", "አሶሳ መገናኛ", 60),
    ("አሶሳ መገናኛ", "አጋሮ", 150),
    ("አጋሮ", "ጅማ", 50),
    ("ጅማ", "ቦንጋ", 110),
    ("ቦንጋ", "ሚዛን አማን", 130),
    ("ጅማ", "ደምቢዶሎ", 220),
    ("ደምቢዶሎ", "ጋምቤላ", 100)
]

# Graph መፍጠር
G = nx.Graph()
for u, v, w in edges_with_distance:
    G.add_edge(u, v, weight=w)

all_locations = sorted(list(G.nodes()))

st.markdown("### 🛣️ ከየትኛውም የአዲስ አበባ ሰፈር ወይም የክልል ከተማ እስከ መድረሻ ያለው ርቀት እና ማቆሚያዎች")
col_start, col_end = st.columns(2)
with col_start:
    start_point = st.selectbox("መነሻ (ሰፈር ወይም ከተማ):", all_locations, index=all_locations.index("AMG Holdings - Gelan") if "AMG Holdings - Gelan" in all_locations else 0, key="start_route_all")
with col_end:
    end_point = st.selectbox("ድረሻ (መድረሻ ሎኬሽን):", all_locations, index=all_locations.index("ድሬዳዋ") if "ድሬዳዋ" in all_locations else min(1, len(all_locations)-1), key="end_route_all")

if st.button("አጠቃላይ መስመሩን፣ ሰፈሮቹን እና ርቀት ፈልግ"):
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
        st.warning(f"⚠️ ከ '{start_point}' እስከ '{end_point}' ያለው ቀጥተኛ የመንገድ ትስስር በዚህ መረብ ውስጥ አልተገኘም።")
    
