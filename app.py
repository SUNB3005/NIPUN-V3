import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="नपुण महाराष्ट्र डॅशबोर्ड", layout="wide")

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
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# --- Sidebar Filters ---
st.sidebar.header("🔍 प्रगत फिल्टर्स")
district = st.sidebar.selectbox("जिल्हा", ['All'] + sorted(df['district'].dropna().unique().tolist()))
df_filtered = df if district == 'All' else df[df['district'] == district]

block = st.sidebar.selectbox("तालुका", ['All'] + sorted(df_filtered['block'].dropna().unique().tolist()))
if block != 'All': df_filtered = df_filtered[df_filtered['block'] == block]

cluster = st.sidebar.selectbox("केंद्र", ['All'] + sorted(df_filtered['cluster'].dropna().unique().tolist()))
if cluster != 'All': df_filtered = df_filtered[df_filtered['cluster'] == cluster]

mgmt = st.sidebar.selectbox("व्यवस्थापन", ['All'] + sorted(df_filtered['management_type'].dropna().unique().tolist()))
if mgmt != 'All': df_filtered = df_filtered[df_filtered['management_type'] == mgmt]

# --- Top Buttons & Metrics ---
col1, col2 = st.columns([8, 2])
with col2:
    if st.button("🖨️ Print / Save PDF"):
        st.write('<script>window.print()</script>', unsafe_allow_html=True)

# KPI Cards
st.subheader("📈 एकत्रित प्रगती अहवाल")
k1, k2, k3, k4 = st.columns(4)
k1.metric("🏫 एकूण शाळा", f"{df_filtered['school'].nunique():,}")
k2.metric("👥 एकूण विद्यार्थी", f"{df_filtered['all Total Student'].sum():,}")
k3.metric("⭐ पूर्ण निपुण (विद्यार्थी)", f"{df_filtered['all all nipun'].sum():,}")
k4.metric("📊 सरासरी प्रगती", f"{df_filtered['all all nipun percentage'].mean():.1f}%")

st.markdown("---")

# --- Tables ---
show_data = st.toggle("📊 Show Data (तपशील पहा)", value=True)

if show_data:
    def get_safe_pct(nipun_col, total_col):
        # inf किंवा NaN ला 0% करतो
        return (df_filtered[nipun_col] / df_filtered[total_col] * 100).fillna(0).replace([float('inf'), -float('inf')], 0).round(1).astype(str) + '%'

    def render_table(class_num):
        data = pd.DataFrame()
        data['SR.NO.'] = range(1, len(df_filtered) + 1)
        data['CLUSTER'] = df_filtered['cluster']
        data['UDISE'] = df_filtered['udise']
        data['SCHOOL'] = df_filtered['school']
        data['MANGEMENT'] = df_filtered['management_type']
        
        prefix = 'all' if class_num == 'All' else f'Class {class_num}'
        total_col = 'all Total Student' if class_num == 'All' else f'class {class_num} Total Student'
        
        data['Total Student'] = df_filtered[total_col]
        data['Reading'] = df_filtered[f'{prefix} reading nipun']
        data['Reading %'] = get_safe_pct(f'{prefix} reading nipun', total_col)
        data['Writing'] = df_filtered[f'{prefix} writing nipun']
        data['Writing %'] = get_safe_pct(f'{prefix} writing nipun', total_col)
        data['Numeracy'] = df_filtered[f'{prefix} numercy nipun']
        data['Numeracy %'] = get_safe_pct(f'{prefix} numercy nipun', total_col)
        data['Operation'] = df_filtered[f'{prefix} operation nipun']
        data['Operation %'] = get_safe_pct(f'{prefix} operation nipun', total_col)
        data['All Nipun'] = df_filtered[f'{prefix} all nipun']
        return data

    for c in [2, 3, 4, 5, 'All']:
        label = f"इयत्ता {c}" if c != 'All' else "सर्व एकत्रित (All Classes)"
        st.subheader(f"📘 {label} तपशील")
        st.dataframe(render_table(c), use_container_width=True)