import streamlit as st
import pandas as pd

# Page Configuration
st.set_page_config(
    page_title="नपुण महाराष्ट्र - प्रगत शाळा व वर्गनिहाय डॅशबोर्ड",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for styling
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
    .metric-card {
        background-color: #f8f9fa;
        border: 1px solid #dee2e6;
        padding: 15px;
        border-radius: 8px;
        text-align: center;
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
    # Column names safe cleaning (strip spaces)
    df.columns = df.columns.str.strip()
    return df

try:
    df = load_data()
except Exception as e:
    st.error(f"डेटा लोड करताना त्रुटी आली: कृपया 'Book9.xlsx' फाईल कोडच्या फोल्डरमध्ये ठेवा. तपशील: {e}")
    st.stop()

# --- Sidebar Filters ---
st.sidebar.header("🔍 प्रगत फिल्टर्स (Filters)")

# 1. District Filter
districts = ['All Districts'] + sorted(df['district'].dropna().unique().tolist())
selected_district = st.sidebar.selectbox("जिल्हा (District)", districts)

if selected_district != 'All Districts':
    df_filtered = df[df['district'] == selected_district]
else:
    df_filtered = df.copy()

# 2. Block Filter
blocks = ['All Blocks'] + sorted(df_filtered['block'].dropna().unique().tolist())
selected_block = st.sidebar.selectbox("तालुका (Block)", blocks)

if selected_block != 'All Blocks':
    df_filtered = df_filtered[df_filtered['block'] == selected_block]

# 3. Cluster Filter
clusters = ['All Clusters'] + sorted(df_filtered['cluster'].dropna().unique().tolist())
selected_cluster = st.sidebar.selectbox("केंद्र (Cluster)", clusters)

if selected_cluster != 'All Clusters':
    df_filtered = df_filtered[df_filtered['cluster'] == selected_cluster]

# 4. Management Type Filter
managements = ['All Managements'] + sorted(df_filtered['management_type'].dropna().unique().tolist())
selected_mgmt = st.sidebar.selectbox("व्यवस्थापन प्रकार (Management Type)", managements)

if selected_mgmt != 'All Managements':
    df_filtered = df_filtered[df_filtered['management_type'] == selected_mgmt]

# 5. Search School Name Filter
school_search = st.sidebar.text_input("शाळेचे नाव शोधा (Search School Name)", "")
if school_search:
    df_filtered = df_filtered[df_filtered['school'].str.contains(school_search, case=False, na=False)]

# 6. Class Selection Filter
class_option = st.sidebar.selectbox(
    "इयत्ता निवडा (Class)", 
    ["सर्व एकत्रित (All Classes)", "इयत्ता २ वी (Class 2)", "इयत्ता ३ वी (Class 3)", "इयत्ता ४ वी (Class 4)", "इयत्ता ५ वी (Class 5)"]
)

# --- KPI Summary Calculations based on Class selection ---
if class_option == "इयत्ता २ वी (Class 2)":
    tot_col, read_col, write_col, num_col, op_col, all_col = 'class 2 Total Student', 'Class 2 reading nipun', 'Class 2 writing nipun', 'Class 2 numercy nipun', 'Class 2 operation nipun', 'Class 2 all nipun'
elif class_option == "इयत्ता ३ वी (Class 3)":
    tot_col, read_col, write_col, num_col, op_col, all_col = 'class 3 Total Student', 'Class 3 reading nipun', 'Class 3 writing nipun', 'Class 3 numercy nipun', 'Class 3 operation nipun', 'Class 3 all nipun'
elif class_option == "इयत्ता ४ वी (Class 4)":
    tot_col, read_col, write_col, num_col, op_col, all_col = 'class 4 Total Student', 'Class 4 reading nipun', 'Class 4 writing nipun', 'Class 4 numercy nipun', 'Class 4 operation nipun', 'Class 4 all nipun'
elif class_option == "इयत्ता ५ वी (Class 5)":
    tot_col, read_col, write_col, num_col, op_col, all_col = 'class 5 Total Student', 'Class 5 reading nipun', 'Class 5 writing nipun', 'Class 5 numercy nipun', 'Class 5 operation nipun', 'Class 5 all nipun'
else:
    tot_col, read_col, write_col, num_col, op_col, all_col = 'all Total Student', 'all reading nipun', 'all writing nipun', 'all numercy nipun', 'all operation nipun', 'all all nipun'

total_students = df_filtered[tot_col].sum() if tot_col in df_filtered.columns else 0
total_read = df_filtered[read_col].sum() if read_col in df_filtered.columns else 0
total_write = df_filtered[write_col].sum() if write_col in df_filtered.columns else 0
total_num = df_filtered[num_col].sum() if num_col in df_filtered.columns else 0
total_op = df_filtered[op_col].sum() if op_col in df_filtered.columns else 0
total_all_nipun = df_filtered[all_col].sum() if all_col in df_filtered.columns else 0

read_pct = (total_read / total_students * 100) if total_students > 0 else 0
write_pct = (total_write / total_students * 100) if total_students > 0 else 0
num_pct = (total_num / total_students * 100) if total_students > 0 else 0
op_pct = (total_op / total_students * 100) if total_students > 0 else 0
all_pct = (total_all_nipun / total_students * 100) if total_students > 0 else 0

# --- Display KPI Summary Cards ---
st.markdown("### 📈 एकत्रित प्रगती अहवाल (Overall KPI Summary)")
col1, col2, col3, col4, col5, col6 = st.columns(6)

with col1:
    st.metric(label="एकूण विद्यार्थी", value=f"{total_students:,}")
with col2:
    st.metric(label="वाचन निपुण", value=f"{total_read:,}", delta=f"{read_pct:.1f}%")
with col3:
    st.metric(label="लेखन निपुण", value=f"{total_write:,}", delta=f"{write_pct:.1f}%")
with col4:
    st.metric(label="संख्याज्ञान निपुण", value=f"{total_num:,}", delta=f"{num_pct:.1f}%")
with col5:
    st.metric(label="क्रिया निपुण", value=f"{total_op:,}", delta=f"{op_pct:.1f}%")
with col6:
    st.metric(label="पूर्ण निपुण (All)", value=f"{total_all_nipun:,}", delta=f"{all_pct:.1f}%")

st.markdown("---")

# --- Detailed School Data Table ---
st.markdown("### 🏫 शाळा निहाय तपशीलवार माहिती (School-wise Details)")

if not df_filtered.empty:
    # Select columns to display neatly
    display_columns = ['district', 'block', 'cluster', 'udise', 'school', 'management_type', tot_col, read_col, write_col, num_col, op_col, all_col]
    available_cols = [c for c in display_columns if c in df_filtered.columns]
    
    st.dataframe(df_filtered[available_cols], use_container_width=True)
    
    # Download Button for Filtered Data
    csv = df_filtered[available_cols].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 फिल्टर केलेला डेटा डाउनलोड करा (Download CSV)",
        data=csv,
        file_name='filtered_nipun_report.csv',
        mime='text/csv',
    )
else:
    st.warning("निवडलेल्या फिल्टर्सनुसार कोणतीही माहिती उपलब्ध नाही.")