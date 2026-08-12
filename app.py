import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(page_title="निपुण महाराष्ट्र डॅशबोर्ड", layout="wide")

# Custom CSS
st.markdown("""
    <style>
    .main-header { font-size: 26px; font-weight: bold; color: #ffffff; background: #d9534f; padding: 15px; border-radius: 8px; text-align: center; }
    </style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 निपुण महाराष्ट्र - प्रगत शाळा डॅशबोर्ड</div>', unsafe_allow_html=True)

# Data Loading
@st.cache_data
def load_data():
    df = pd.read_excel('Book9.xlsx') # तुमची फाईल नेम
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Sidebar Filters
st.sidebar.header("🔍 फिल्टर्स")
district = st.sidebar.selectbox("जिल्हा", ['All'] + sorted(df['district'].dropna().unique().tolist()))
df_filtered = df if district == 'All' else df[df['district'] == district]

# Safe Percentage Calculation Function
def get_safe_pct(nipun_col, total_col):
    # nipun / total * 100, replace inf/NaN with 0
    series = (df_filtered[nipun_col] / df_filtered[total_col] * 100)
    return series.fillna(0).replace([float('inf'), -float('inf')], 0).round(1).astype(str) + '%'

# --- Main Dashboard ---
total_schools = df_filtered['school'].nunique()
st.metric("🏫 एकूण शाळा", f"{total_schools:,}")

# Tables Generator
def render_class_table(class_num):
    data = pd.DataFrame()
    data['SR.NO.'] = range(1, len(df_filtered) + 1)
    data['CLUSTER'] = df_filtered['cluster']
    data['UDISE'] = df_filtered['udise']
    data['SCHOOL'] = df_filtered['school']
    data['MANAGEMENT'] = df_filtered['management_type']
    
    if class_num == 'All':
        prefix = 'all'
        total_col = 'all Total Student'
    else:
        prefix = f'Class {class_num}'
        total_col = f'class {class_num} Total Student'
        
    # Columns Logic
    data['Total'] = df_filtered[total_col]
    data['Reading'] = df_filtered[f'{prefix} reading nipun']
    data['Reading %'] = get_safe_pct(f'{prefix} reading nipun', total_col)
    data['Writing'] = df_filtered[f'{prefix} writing nipun']
    data['Writing %'] = get_safe_pct(f'{prefix} writing nipun', total_col)
    data['Numeracy'] = df_filtered[f'{prefix} numercy nipun']
    data['Numeracy %'] = get_safe_pct(f'{prefix} numercy nipun', total_col)
    data['Operation'] = df_filtered[f'{prefix} operation nipun']
    data['Operation %'] = get_safe_pct(f'{prefix} operation nipun', total_col)
    
    return data

# Dashboard Sections
show_data = st.checkbox("📊 Show Data", value=True)
if show_data:
    for c in [2, 3, 4, 5, 'All']:
        label = f"इयत्ता {c}" if c != 'All' else "सर्व एकत्रित"
        st.subheader(f"📘 {label} तपशील")
        st.dataframe(render_class_table(c), use_container_width=True)

# Print Button
if st.button("🖨️ Print / Save PDF"):
    st.info("कृपया तुमच्या ब्राउझरमधील Print सेटिंग (Ctrl+P) वापरा.")