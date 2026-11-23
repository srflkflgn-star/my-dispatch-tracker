G, source=start_point, target=end_point, weight='weight')
        
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

    
