import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="निपुण महाराष्ट्र डॅशबोर्ड", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #ffffff; background: linear-gradient(90deg, #d9534f, #f0ad4e); padding: 15px; border-radius: 8px; text-align: center; margin-bottom: 20px; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 निपुण महाराष्ट्र - प्रगत शाळा व वर्गनिहाय डॅशबोर्ड</div>', unsafe_allow_html=True)

# Data Loading
@st.cache_data
def load_data():
    df = pd.read_excel('Book9.xlsx')
    # Clean all string columns to avoid mismatch due to spaces
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].astype(str).str.strip()
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"फाइल लोड करताना एरर आली: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 प्रगत फिल्टर्स")

# 1. District
districts = ['All'] + sorted([str(x) for x in df['district'].dropna().unique() if x != 'nan'])
selected_district = st.sidebar.selectbox("जिल्हा", districts)
df_filtered = df if selected_district == 'All' else df[df['district'] == selected_district]

# 2. Block
blocks = ['All'] + sorted([str(x) for x in df_filtered['block'].dropna().unique() if x != 'nan'])
selected_block = st.sidebar.selectbox("तालुका", blocks)
if selected_block != 'All':
    df_filtered = df_filtered[df_filtered['block'] == selected_block]

# 3. Cluster
clusters = ['All'] + sorted([str(x) for x in df_filtered['cluster'].dropna().unique() if x != 'nan'])
selected_cluster = st.sidebar.selectbox("केंद्र", clusters)
if selected_cluster != 'All':
    df_filtered = df_filtered[df_filtered['cluster'] == selected_cluster]

# 4. Management Type
managements = ['All'] + sorted([str(x) for x in df_filtered['management_type'].dropna().unique() if x != 'nan'])
selected_mgmt = st.sidebar.selectbox("व्यवस्थापन", managements)
if selected_mgmt != 'All':
    df_filtered = df_filtered[df_filtered['management_type'] == selected_mgmt]

# School Search
school_search = st.sidebar.text_input("शाळेचे नाव शोधा", "")
if school_search:
    df_filtered = df_filtered[df_filtered['school'].str.contains(school_search, case=False, na=False)]

# --- Top Buttons & Metrics ---
col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🖨️ Print / Save PDF"):
        st.write('<script>window.print()</script>', unsafe_allow_html=True)

# KPI Cards
st.subheader("📈 एकत्रित प्रगती अहवाल")
k1, k2, k3, k4 = st.columns(4)

total_schools = df_filtered['school'].nunique() if not df_filtered.empty else 0
total_students = pd.to_numeric(df_filtered['all Total Student'], errors='coerce').sum() if not df_filtered.empty else 0
total_nipun = pd.to_numeric(df_filtered['all all nipun'], errors='coerce').sum() if not df_filtered.empty else 0
avg_pct = pd.to_numeric(df_filtered['all all nipun percentage'], errors='coerce').mean() if not df_filtered.empty else 0

k1.metric("🏫 एकूण शाळा", f"{total_schools:,}")
k2.metric("👥 एकूण विद्यार्थी", f"{int(total_students):,}")
k3.metric("⭐ पूर्ण निपुण (विद्यार्थी)", f"{int(total_nipun):,}")
k4.metric("📊 सरासरी प्रगती", f"{avg_pct:.1f}%")

st.markdown("---")

# --- Tables ---
show_data = st.toggle("📊 Show Data (तपशील पहा)", value=True)

if show_data:
    if df_filtered.empty:
        st.warning("⚠️ निवडलेल्या फिल्टर्सनुसार (तालुका/केंद्र) कोणतीही माहिती उपलब्ध नाही.")
    else:
        def get_safe_pct(nipun_col, total_col):
            nipun = pd.to_numeric(df_filtered[nipun_col], errors='coerce').fillna(0)
            tot = pd.to_numeric(df_filtered[total_col], errors='coerce').fillna(0)
            res = (nipun / tot * 100).fillna(0).replace([float('inf'), -float('inf')], 0).round(1)
            return res.astype(str) + '%'

        def render_table(class_num):
            data = pd.DataFrame()
            data['SR.NO.'] = range(1, len(df_filtered) + 1)
            data['CLUSTER'] = df_filtered['cluster']
            data['UDISE'] = df_filtered['udise']
            data['SCHOOL'] = df_filtered['school']
            data['MANGEMENT'] = df_filtered['management_type']
            
            prefix = 'all' if class_num == 'All' else f'Class {class_num}'
            total_col = 'all Total Student' if class_num == 'All' else f'class {class_num} Total Student'
            
            data['Total Student'] = pd.to_numeric(df_filtered[total_col], errors='coerce').fillna(0).astype(int)
            data['Reading'] = pd.to_numeric(df_filtered[f'{prefix} reading nipun'], errors='coerce').fillna(0).astype(int)
            data['Reading %'] = get_safe_pct(f'{prefix} reading nipun', total_col)
            data['Writing'] = pd.to_numeric(df_filtered[f'{prefix} writing nipun'], errors='coerce').fillna(0).astype(int)
            data['Writing %'] = get_safe_pct(f'{prefix} writing nipun', total_col)
            data['Numeracy'] = pd.to_numeric(df_filtered[f'{prefix} numercy nipun'], errors='coerce').fillna(0).astype(int)
            data['Numeracy %'] = get_safe_pct(f'{prefix} numercy nipun', total_col)
            data['Operation'] = pd.to_numeric(df_filtered[f'{prefix} operation nipun'], errors='coerce').fillna(0).astype(int)
            data['Operation %'] = get_safe_pct(f'{prefix} operation nipun', total_col)
            data['All Nipun'] = pd.to_numeric(df_filtered[f'{prefix} all nipun'], errors='coerce').fillna(0).astype(int)
            return data

        for c in [2, 3, 4, 5, 'All']:
            label = f"इयत्ता {c}" if c != 'All' else "सर्व एकत्रित (All Classes)"
            st.subheader(f"📘 {label} तपशील")
            st.dataframe(render_table(c), use_container_width=True)