import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="निपुण महाराष्ट्र - प्रगत शाळा व वर्गनिहाय डॅशबोर्ड",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling tables and cards like the reference image
st.markdown("""
    <style>
    .main-header {
        font-size: 26px;
        font-weight: bold;
        color: #ffffff;
        background: linear-gradient(90deg, #d9534f, #f0ad4e);
        padding: 15px;
        border-radius: 8px;
        text-align: center;
        margin-bottom: 20px;
    }
    .sub-table-header {
        background-color: #555555;
        color: white;
        padding: 8px;
        text-align: center;
        font-weight: bold;
        border-radius: 4px 4px 0px 0px;
        margin-top: 20px;
    }
    @media print {
        .stSidebar {display: none;}
        .stButton {display: none;}
    }
    </style>
""", unsafe_allow_html=True)

# Title Header
st.markdown('<div class="main-header">📊 निपुण महाराष्ट्र - प्रगत शाळा व वर्गनिहाय डॅशबोर्ड</div>', unsafe_allow_html=True)

# Load Data
@st.cache_data
def load_data():
    file_path = 'Book9.xlsx'
    xls = pd.ExcelFile(file_path)
    df = pd.read_excel(file_path, sheet_name=xls.sheet_names[0])
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"डेटा लोड करताना त्रुटी आली: कृपया 'Book9.xlsx' फाईल कोडच्या फोल्डरमध्ये ठेवा. तपशील: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 प्रगत फिल्टर्स (Filters)")

districts = ['All Districts'] + sorted(df['district'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("जिल्हा (District)", districts)
df_filtered = df[df['district'] == selected_district] if selected_district != 'All Districts' else df.copy()

blocks = ['All Blocks'] + sorted(df_filtered['block'].dropna().unique().tolist())
selected_block = st.sidebar.selectbox("तालुका (Block)", blocks)
if selected_block != 'All Blocks':
    df_filtered = df_filtered[df_filtered['block'] == selected_block]

clusters = ['All Clusters'] + sorted(df_filtered['cluster'].dropna().unique().tolist())
selected_cluster = st.sidebar.selectbox("केंद्र (Cluster)", clusters)
if selected_cluster != 'All Clusters':
    df_filtered = df_filtered[df_filtered['cluster'] == selected_cluster]

managements = ['All Managements'] + sorted(df_filtered['management_type'].dropna().unique().tolist())
selected_mgmt = st.sidebar.selectbox("व्यवस्थापन प्रकार (Management Type)", managements)
if selected_mgmt != 'All Managements':
    df_filtered = df_filtered[df_filtered['management_type'] == selected_mgmt]

school_search = st.sidebar.text_input("शाळेचे नाव शोधा (Search School Name)", "")
if school_search:
    df_filtered = df_filtered[df_filtered['school'].str.contains(school_search, case=False, na=False)]

# --- Top Action Buttons & Metrics ---
col_btn1, col_btn2 = st.columns([8, 2])
with col_btn2:
    if st.button("🖨️ Print / Save PDF"):
        st.markdown("<script>window.print();</script>", unsafe_allow_html=True)

# Calculate Totals & Schools Count
total_schools = df_filtered['school'].nunique()
total_students = df_filtered['all Total Student'].sum() if 'all Total Student' in df_filtered.columns else 0
total_all_nipun = df_filtered['all all nipun'].sum() if 'all all nipun' in df_filtered.columns else 0
all_pct = (total_all_nipun / total_students * 100) if total_students > 0 else 0

# --- Display KPI Summary Cards (Including 'एकूण शाळा') ---
st.markdown("### 📈 एकत्रित प्रगती अहवाल (Overall KPI Summary)")
kpi1, kpi2, kpi3, kpi4, kpi5, kpi6 = st.columns(6)

with kpi1:
    st.metric(label="🏫 एकूण शाळा", value=f"{total_schools:,}")
with kpi2:
    st.metric(label="👥 एकूण विद्यार्थी", value=f"{total_students:,}")
with kpi3:
    st.metric(label="📖 वाचन निपुण", value=f"{df_filtered['all reading nipun'].sum() if 'all reading nipun' in df_filtered.columns else 0:,}")
with kpi4:
    st.metric(label="✍️ लेखन निपुण", value=f"{df_filtered['all writing nipun'].sum() if 'all writing nipun' in df_filtered.columns else 0:,}")
with kpi5:
    st.metric(label="🔢 संख्याज्ञान निपुण", value=f"{df_filtered['all numercy nipun'].sum() if 'all numercy nipun' in df_filtered.columns else 0:,}")
with kpi6:
    st.metric(label="⭐ पूर्ण निपुण (All)", value=f"{total_all_nipun:,}", delta=f"{all_pct:.1f}%")

st.markdown("---")

# --- Show Data Toggle Button ---
show_data_toggle = st.toggle("📊 Show Data (तपशीलवार टेबल पहा)", value=True)

if show_data_toggle:
    st.markdown("### 🏫 वर्गनिहाय आणि प्रतिमा रचनेनुसार तपशीलवार टेबल्स (Class-wise Assessment Tables)")

    if not df_filtered.empty:
        # Helper function to generate standardized formatted tables matching the image layout
        def create_class_table(class_num):
            temp_df = pd.DataFrame()
            temp_df['SR.NO.'] = range(1, len(df_filtered) + 1)
            temp_df['CLUSTER'] = df_filtered['cluster']
            temp_df['UDISE'] = df_filtered['udise']
            temp_df['SCHOOL'] = df_filtered['school']
            temp_df['MANGEMENT'] = df_filtered['management_type']
            
            if class_num in [2, 3, 4, 5]:
                prefix = f'Class {class_num}'
                temp_df[f'Class {class_num} Total Student'] = df_filtered.get(f'{prefix} Total Student', 0)
                temp_df[f'Class {class_num} reading nipun'] = df_filtered.get(f'{prefix} reading nipun', 0)
                
                # Calculate Percentages safely
                tot = temp_df[f'Class {class_num} Total Student']
                temp_df['Reading %'] = (df_filtered.get(f'{prefix} reading nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df[f'Class {class_num} writing nipun'] = df_filtered.get(f'{prefix} writing nipun', 0)
                temp_df['Writing %'] = (df_filtered.get(f'{prefix} writing nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df[f'Class {class_num} numercy nipun'] = df_filtered.get(f'{prefix} numercy nipun', 0)
                temp_df['Numeracy %'] = (df_filtered.get(f'{prefix} numercy nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df[f'Class {class_num} operation nipun'] = df_filtered.get(f'{prefix} operation nipun', 0)
                temp_df['Operation %'] = (df_filtered.get(f'{prefix} operation nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df[f'Class {class_num} all nipun'] = df_filtered.get(f'{prefix} all nipun', 0)
                temp_df[f'Class {class_num} all nipun %'] = (df_filtered.get(f'{prefix} all nipun percentage', 0)).fillna(0).round(1).astype(str) + '%'
            
            else: # All Classes Combined Table
                temp_df['All Total Student'] = df_filtered.get('all Total Student', 0)
                temp_df['All reading nipun'] = df_filtered.get('all reading nipun', 0)
                tot = temp_df['All Total Student']
                temp_df['Reading %'] = (df_filtered.get('all reading nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df['All writing nipun'] = df_filtered.get('all writing nipun', 0)
                temp_df['Writing %'] = (df_filtered.get('all writing nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df['All numeracy nipun'] = df_filtered.get('all numercy nipun', 0)
                temp_df['Numeracy %'] = (df_filtered.get('all numercy nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df['All operation nipun'] = df_filtered.get('all operation nipun', 0)
                temp_df['Operation %'] = (df_filtered.get('all operation nipun', 0) / tot * 100).fillna(0).round(1).astype(str) + '%'
                
                temp_df['All all nipun'] = df_filtered.get('all all nipun', 0)
                temp_df['All Class Nipun %'] = (df_filtered.get('all all nipun percentage', 0)).fillna(0).round(1).astype(str) + '%'

            return temp_df

        # Render Tables for Class 2, 3, 4, 5 and All Classes matching image layout
        for c_val in [2, 3, 4, 5]:
            st.markdown(f"#### 📘 इयत्ता {c_val} वी तपशीलवार माहिती")
            st.dataframe(create_class_table(c_val), use_container_width=True)

        st.markdown(f"#### 📚 सर्व वर्ग एकत्रित तपशीलवार माहिती (All Classes Combined)")
        st.dataframe(create_class_table('all'), use_container_width=True)
        
        # Download Button
        csv = df_filtered.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 सर्व डेटा CSV मध्ये डाउनलोड करा",
            data=csv,
            file_name='nipun_all_classes_report.csv',
            mime='text/csv',
        )
    else:
        st.warning("निवडलेल्या फिल्टर्सनुसार कोणतीही माहिती उपलब्ध नाही.")