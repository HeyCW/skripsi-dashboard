import streamlit as st
import pandas as pd
import numpy as np
import gspread
from google.oauth2.service_account import Credentials
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Page config
st.set_page_config(
    page_title="Dashboard Analitik Mahasiswa",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .success-box {
        background-color: #d4edda;
        border-left: 4px solid #28a745;
        padding: 1rem;
        margin: 1rem 0;
    }
    .warning-box {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 1rem;
        margin: 1rem 0;
    }
    .danger-box {
        background-color: #f8d7da;
        border-left: 4px solid #dc3545;
        padding: 1rem;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# --- CONFIG ---
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']

# Multiple Sheets Configuration
SHEETS_CONFIG = {
    "Redis List/Set": "https://docs.google.com/spreadsheets/d/1By9e0g-aFr3A37lvdSBNeE2BEwmzuTkePPm_Z2UzJYQ/edit?gid=0#gid=0",
    "Redis Timeseries": "https://docs.google.com/spreadsheets/d/1xTbhdaVwCeKdrWcHTEbrGFBQtgWq8q3f5PVNigc3CZc/edit?gid=0#gid=0",
    "MongoDB": "https://docs.google.com/spreadsheets/d/1tIVhazaxOiow9o0Am5TszA3nFUl37h3hk2Li_8vcgpQ/edit?gid=0#gid=0",
    "Neo4J": "https://docs.google.com/spreadsheets/d/17mIrxz5hMNXAcCLqLDTAZ0NGSlMOo15AL1XjcBBzGzA/edit?gid=0#gid=0",
    "Big Data Assignment 1": "https://docs.google.com/spreadsheets/d/1_zcW_nSwNm9T4os8PuMAcK_3wS2MhEl9B_SDET8GkxI/edit?gid=0#gid=0",
    "Big Data Assignment 2": "https://docs.google.com/spreadsheets/d/1HwPfWW5I3kYRfY91QH9GWsr6s_obZCT1j9W03W4g4Cs/edit?gid=0#gid=0",
    "Big Data Assignment 3": "https://docs.google.com/spreadsheets/d/1AlnkwRg_6WU-zr5yreWPDkAPEXU_mzrBfIUIt2DXwzM/edit?gid=0#gid=0"
}

def get_credentials():
    """Get Google Sheets credentials from Streamlit secrets"""
    try:
        # Check if gcp_service_account exists in secrets
        if "gcp_service_account" not in st.secrets:
            raise Exception(
                "❌ Service Account tidak ditemukan!\n\n"
                "Untuk Streamlit Cloud:\n"
                "1. Buka Settings > Secrets di dashboard Streamlit Cloud\n"
                "2. Tambahkan credentials dengan format:\n\n"
                "[gcp_service_account]\n"
                'type = "service_account"\n'
                'project_id = "your-project-id"\n'
                'private_key_id = "your-key-id"\n'
                'private_key = """-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----"""\n'
                'client_email = "your-service-account@project.iam.gserviceaccount.com"\n'
                'client_id = "123456789"\n'
                'token_uri = "https://oauth2.googleapis.com/token"\n\n'
                "3. Share Google Sheets ke service account email!"
            )
        
        # Convert secrets to dictionary
        credentials_dict = dict(st.secrets["gcp_service_account"])
        
        # Create credentials
        creds = Credentials.from_service_account_info(
            credentials_dict,
            scopes=SCOPES
        )
        
        return creds
        
    except Exception as e:
        raise Exception(f"Error loading credentials: {str(e)}")

# Initialize authentication
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False
    st.session_state.creds = None

# Auth section
if not st.session_state.authenticated:
    st.markdown('<div class="main-header">📊 Dashboard Analitik Mahasiswa</div>', unsafe_allow_html=True)
    
    st.info("🔐 Connecting to Google Sheets...")
    
    # Show setup instructions
    with st.expander("📖 Setup Instructions untuk Streamlit Cloud"):
        st.markdown("""
        ## Setup Service Account untuk Streamlit Cloud
        
        ### 1️⃣ Buat Service Account di Google Cloud Console
        
        1. Buka [Google Cloud Console](https://console.cloud.google.com/)
        2. Buat project baru atau pilih existing project
        3. Buka **IAM & Admin > Service Accounts**
        4. Klik **Create Service Account**
        5. Beri nama (contoh: `sheets-reader`)
        6. Klik **Create and Continue**
        7. Skip role assignment (klik **Continue**)
        8. Klik **Done**
        
        ### 2️⃣ Generate JSON Key
        
        1. Klik service account yang baru dibuat
        2. Tab **Keys** > **Add Key** > **Create new key**
        3. Pilih **JSON** dan klik **Create**
        4. File JSON akan terdownload
        
        ### 3️⃣ Enable Google Sheets API
        
        1. Di Google Cloud Console, buka **APIs & Services > Library**
        2. Search "Google Sheets API"
        3. Klik dan **Enable**
        
        ### 4️⃣ Share Google Sheets
        
        1. Buka Google Sheets yang ingin diakses
        2. Klik **Share**
        3. Copy **client_email** dari file JSON (format: `xxx@xxx.iam.gserviceaccount.com`)
        4. Paste ke share dialog dan beri akses **Viewer**
        5. Ulangi untuk semua sheets yang ingin diakses
        
        ### 5️⃣ Tambahkan ke Streamlit Cloud Secrets
        
        1. Buka app di Streamlit Cloud
        2. Settings > Secrets
        3. Copy format berikut dan isi dengan data dari JSON:
        
        ```toml
        [gcp_service_account]
        type = "service_account"
        project_id = "your-project-id"
        private_key_id = "your-private-key-id"
        private_key = '''-----BEGIN PRIVATE KEY-----
        MIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...
        ...
        -----END PRIVATE KEY-----'''
        client_email = "your-service-account@your-project.iam.gserviceaccount.com"
        client_id = "123456789012345678901"
        auth_uri = "https://accounts.google.com/o/oauth2/auth"
        token_uri = "https://oauth2.googleapis.com/token"
        auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
        client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com"
        ```
        
        **PENTING:**
        - Gunakan triple quotes `'''` untuk private_key
        - Jangan tambahkan `\\n`, gunakan line breaks asli
        - Pastikan tidak ada spasi ekstra di awal/akhir
        
        ### 6️⃣ Test Connection
        
        Klik tombol **Connect to Google Sheets** di bawah!
        """)
    
    # Debug info
    with st.expander("🔧 Debug - Credentials Status"):
        st.write("**Secrets Configuration Status:**")
        
        if "gcp_service_account" in st.secrets:
            st.success("✅ Service Account config found!")
            try:
                sa_email = st.secrets['gcp_service_account']['client_email']
                st.write(f"**Service Account Email:** `{sa_email}`")
                st.info("⚠️ PENTING: Pastikan semua Google Sheets sudah di-share ke email ini dengan akses Viewer!")
                
                # Check required fields
                required_fields = ['type', 'project_id', 'private_key_id', 'private_key', 
                                 'client_email', 'client_id', 'token_uri']
                missing_fields = [field for field in required_fields 
                                if field not in st.secrets['gcp_service_account']]
                
                if missing_fields:
                    st.error(f"❌ Missing fields: {', '.join(missing_fields)}")
                else:
                    st.success("✅ All required fields present")
                    
                # Check private key format
                pk = st.secrets['gcp_service_account']['private_key']
                if '-----BEGIN PRIVATE KEY-----' in pk and '-----END PRIVATE KEY-----' in pk:
                    st.success("✅ Private key format looks good")
                else:
                    st.error("❌ Private key format error - harus ada BEGIN dan END markers")
                    
            except Exception as e:
                st.error(f"❌ Error checking config: {e}")
        else:
            st.error("❌ Service Account config NOT found!")
            st.write("Tambahkan `[gcp_service_account]` di Streamlit Cloud Secrets")
            st.write("Path: Settings > Secrets di Streamlit Cloud dashboard")
    
    if st.button("🔐 Connect to Google Sheets", type="primary"):
        try:
            with st.spinner("Connecting to Google Sheets..."):
                st.session_state.creds = get_credentials()
                
                # Test connection
                client = gspread.authorize(st.session_state.creds)
                
                st.session_state.authenticated = True
            
            st.success("✅ Connected successfully!")
            st.balloons()
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Connection failed!")
            st.error(str(e))
            
            st.info(
                "💡 Troubleshooting Tips:\n\n"
                "1. Pastikan Service Account sudah dibuat di Google Cloud Console\n"
                "2. Pastikan Google Sheets API sudah di-enable\n"
                "3. Pastikan semua Google Sheets sudah di-share ke service account email\n"
                "4. Pastikan format secrets.toml benar (lihat contoh di atas)\n"
                "5. Pastikan private_key menggunakan triple quotes dan tanpa \\n\n"
                "Cek debug panel di atas untuk detail lebih lanjut."
            )
    
    st.stop()

# Main App
st.markdown('<div class="main-header">📊 Dashboard Analitik Mahasiswa</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/student-male.png", width=80)
    st.title("Navigation")
    
    page = st.radio(
        "Pilih Dashboard:",
        [
            "Overview",
            "Submission History",
            "Analisis Performa",
            "Pattern Submission",
            "Dashboard Dosen",
            "Predictive Analytics",
            "Custom Analytics",
            "Compare Assignments"
        ]
    )
    
    st.divider()
    
    # Assignment selector
    st.subheader("📚 Pilih Assignment")
    selected_assignments = st.multiselect(
        "Assignment:",
        options=list(SHEETS_CONFIG.keys()),
        default=[list(SHEETS_CONFIG.keys())[0]],
        help="Pilih satu atau lebih assignment untuk dianalisis"
    )
    
    # View mode for multiple assignments
    if len(selected_assignments) == 1:
        view_mode = "single"
    else:
        view_mode = st.radio(
            "View Mode:",
            ["Individual", "Combined"],
            help="Individual: Lihat per assignment | Combined: Gabungkan semua data"
        )
    
    st.divider()
    
    # Refresh button
    if st.button("🔄 Refresh Data", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.divider()
    
    # Show connection status
    st.success("✅ Connected")
    
    # Logout button
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        st.session_state.creds = None
        st.rerun()

@st.cache_data(ttl=300)
def load_data_from_gsheet(_creds, sheet_url):
    """Load data dari Google Sheets"""
    try:
        client = gspread.authorize(_creds)
        sheet = client.open_by_url(sheet_url)
        worksheet = sheet.get_worksheet(0)
        data = worksheet.get_all_records()
        df = pd.DataFrame(data)
        
        # Data preprocessing
        if "Date" in df.columns:
            df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
            df = df.dropna(subset=["Date"])
            df = df.sort_values("Date")
        
        if "Nilai" in df.columns:
            df["Nilai"] = pd.to_numeric(df["Nilai"], errors="coerce")
        
        return df
    except Exception as e:
        st.error(f"Gagal load data: {e}")
        return None

def load_multiple_sheets(creds, assignments):
    """Load data from multiple sheets"""
    all_data = {}
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    for idx, assignment in enumerate(assignments):
        status_text.text(f"Loading {assignment}...")
        sheet_url = SHEETS_CONFIG[assignment]
        df = load_data_from_gsheet(creds, sheet_url)
        if df is not None:
            df['Assignment'] = assignment
            all_data[assignment] = df
        progress_bar.progress((idx + 1) / len(assignments))
    
    progress_bar.empty()
    status_text.empty()
    
    return all_data

def combine_dataframes(data_dict):
    """Combine multiple dataframes into one"""
    if not data_dict:
        return None
    
    combined = pd.concat(data_dict.values(), ignore_index=True)
    return combined

def calculate_metrics(df):
    """Calculate various metrics from dataframe"""
    metrics = {}
    
    # Basic metrics
    metrics['total_submissions'] = len(df)
    metrics['unique_students'] = df['NRP'].nunique()
    metrics['pass_rate'] = (df['Status'] == 'Lulus').sum() / len(df) * 100 if len(df) > 0 else 0
    metrics['avg_score'] = df['Nilai'].mean() if len(df) > 0 else 0
    
    # Student-level metrics
    student_stats = df.groupby('NRP').agg({
        'Nilai': ['mean', 'max', 'count'],
        'Status': lambda x: (x == 'Lulus').any()
    }).reset_index()
    student_stats.columns = ['NRP', 'avg_score', 'max_score', 'attempts', 'passed']
    
    metrics['students_passed'] = student_stats['passed'].sum()
    metrics['students_not_passed'] = len(student_stats) - metrics['students_passed']
    metrics['avg_attempts'] = student_stats['attempts'].mean() if len(student_stats) > 0 else 0
    metrics['student_stats'] = student_stats
    
    return metrics

def plot_score_distribution(df):
    """Plot score distribution"""
    fig = px.histogram(
        df, 
        x='Nilai', 
        nbins=20,
        title='Distribusi Nilai',
        color_discrete_sequence=['#1f77b4']
    )
    fig.update_layout(
        xaxis_title='Nilai',
        yaxis_title='Jumlah Submission',
        showlegend=False
    )
    return fig

def plot_submission_timeline(df):
    """Plot submission timeline"""
    daily_submissions = df.groupby(df['Date'].dt.date).size().reset_index()
    daily_submissions.columns = ['Date', 'Count']
    
    fig = px.line(
        daily_submissions,
        x='Date',
        y='Count',
        title='Timeline Submission',
        markers=True
    )
    fig.update_layout(
        xaxis_title='Tanggal',
        yaxis_title='Jumlah Submission'
    )
    return fig

def plot_pass_rate_by_student(df):
    """Plot pass rate by student"""
    student_pass = df.groupby('NRP').agg({
        'Status': lambda x: (x == 'Lulus').sum() / len(x) * 100
    }).reset_index()
    student_pass.columns = ['NRP', 'Pass Rate']
    student_pass = student_pass.sort_values('Pass Rate', ascending=True)

    fig = px.bar(
        student_pass,
        x='Pass Rate',
        y='NRP',
        orientation='h',
        title='Pass Rate per Mahasiswa',
        color='Pass Rate',
        color_continuous_scale='RdYlGn'
    )

    fig.update_yaxes(
        automargin=True,
        tickmode='linear'
    )
    fig.update_layout(
        xaxis_title='Pass Rate (%)',
        yaxis_title='NRP',
        height=max(400, len(student_pass) * 20),
        margin=dict(l=200)
    )
    return fig

def plot_submission_heatmap(df):
    """Plot submission heatmap by hour and day"""
    df['Hour'] = df['Date'].dt.hour
    df['DayOfWeek'] = df['Date'].dt.day_name()
    
    heatmap_data = df.groupby(['DayOfWeek', 'Hour']).size().reset_index()
    heatmap_data.columns = ['DayOfWeek', 'Hour', 'Count']
    
    # Order days
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    heatmap_pivot = heatmap_data.pivot(index='DayOfWeek', columns='Hour', values='Count').fillna(0)
    heatmap_pivot = heatmap_pivot.reindex(day_order)
    
    fig = px.imshow(
        heatmap_pivot,
        title='Heatmap Waktu Submission',
        labels=dict(x="Jam", y="Hari", color="Jumlah"),
        color_continuous_scale='Blues'
    )
    return fig

def plot_attempts_before_pass(df):
    """Plot number of attempts before passing"""
    passed_students = df[df['Status'] == 'Lulus'].groupby('NRP').first().reset_index()
    
    attempts_data = []
    for nrp in passed_students['NRP']:
        student_data = df[df['NRP'] == nrp].sort_values('Date')
        first_pass_date = student_data[student_data['Status'] == 'Lulus']['Date'].iloc[0]
        attempts_before_pass = len(student_data[student_data['Date'] <= first_pass_date])
        attempts_data.append({'NRP': nrp, 'Attempts': attempts_before_pass})
    
    attempts_df = pd.DataFrame(attempts_data)
    
    fig = px.histogram(
        attempts_df,
        x='Attempts',
        title='Distribusi Jumlah Attempt Sebelum Lulus',
        nbins=10
    )
    fig.update_layout(
        xaxis_title='Jumlah Attempt',
        yaxis_title='Jumlah Mahasiswa'
    )
    return fig

def plot_score_progress(df, nrp):
    """Plot score progress for a specific student"""
    student_data = df[df['NRP'] == nrp].sort_values('Date')
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=student_data['Date'],
        y=student_data['Nilai'],
        mode='lines+markers',
        name='Nilai',
        line=dict(color='#1f77b4', width=2),
        marker=dict(size=8)
    ))
    
    fig.add_hline(y=60, line_dash="dash", line_color="green", 
                  annotation_text="Batas Lulus (60)")
    
    fig.update_layout(
        title=f'Progress Nilai - {nrp}',
        xaxis_title='Waktu',
        yaxis_title='Nilai',
        hovermode='x unified'
    )
    
    return fig

def predict_pass_probability(df, nrp):
    """Simple prediction of pass probability based on attempt pattern"""
    student_data = df[df['NRP'] == nrp].sort_values('Date')
    
    if len(student_data) < 2:
        return 50.0
    
    scores = student_data['Nilai'].values
    attempts = np.arange(len(scores))
    
    if len(scores) > 1:
        slope = np.polyfit(attempts, scores, 1)[0]
        avg_score = scores.mean()
        last_score = scores[-1]
        
        if last_score >= 60:
            return 100.0
        elif slope > 5:
            return min(95.0, 50 + slope * 5)
        elif slope > 0:
            return min(70.0, 40 + avg_score / 2)
        else:
            return max(20.0, avg_score / 2)
    
    return 50.0

# Main content based on selected page
if selected_assignments:
    # Load data for selected assignments
    with st.spinner("Loading data from Google Sheets..."):
        all_data = load_multiple_sheets(st.session_state.creds, selected_assignments)
    
    if not all_data:
        st.error("❌ Tidak ada data yang berhasil dimuat")
        st.info("Pastikan:\n1. Google Sheets sudah di-share ke service account email\n2. Sheet memiliki data yang valid\n3. Format data sesuai (kolom: NRP, Date, Nilai, Status)")
        st.stop()
    
    # Determine which dataframe to use
    if len(selected_assignments) == 1:
        df = all_data[selected_assignments[0]]
        current_assignment = selected_assignments[0]
    else:
        if view_mode == "Combined":
            df = combine_dataframes(all_data)
            current_assignment = "Combined View"
        else:
            current_assignment = st.selectbox(
                "Lihat assignment:",
                selected_assignments
            )
            df = all_data[current_assignment]
    
    if df is not None and not df.empty:
        # Show current view info
        st.info(f"📊 Viewing: **{current_assignment}** | Total Records: **{len(df):,}** | Last Updated: **{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}**")
        
        metrics = calculate_metrics(df)
        
        # PAGE: OVERVIEW
        if page == "Overview":
            st.header("📊 Overview Dashboard")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric(
                    "Total Submission",
                    f"{metrics['total_submissions']:,}",
                    help="Total semua submission yang masuk"
                )
            
            with col2:
                st.metric(
                    "Mahasiswa Aktif",
                    metrics['unique_students'],
                    help="Jumlah mahasiswa yang sudah submit"
                )
            
            with col3:
                st.metric(
                    "Pass Rate",
                    f"{metrics['pass_rate']:.1f}%",
                    help="Persentase submission yang lulus"
                )
            
            with col4:
                st.metric(
                    "Rata-rata Nilai",
                    f"{metrics['avg_score']:.1f}",
                    help="Rata-rata nilai dari semua submission"
                )
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(plot_score_distribution(df), use_container_width=True)
            
            with col2:
                st.plotly_chart(plot_submission_timeline(df), use_container_width=True)
            
            st.subheader("👥 Status Mahasiswa")
            col1, col2 = st.columns(2)
            
            with col1:
                fig = go.Figure(data=[go.Pie(
                    labels=['Sudah Lulus', 'Belum Lulus'],
                    values=[metrics['students_passed'], metrics['students_not_passed']],
                    hole=.3,
                    marker_colors=['#28a745', '#dc3545']
                )])
                fig.update_layout(title='Status Kelulusan Mahasiswa')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.metric("Mahasiswa Lulus", metrics['students_passed'])
                st.metric("Mahasiswa Belum Lulus", metrics['students_not_passed'])
                st.metric("Rata-rata Attempt", f"{metrics['avg_attempts']:.1f}")
        
        # PAGE: SUBMISSION HISTORY
        elif page == "Submission History":
            st.header("📈 Submission History")
            
            st.subheader("🏆 Leaderboard")
            
            leaderboard = df.groupby('NRP').agg({
                'Nilai': 'max',
                'Date': 'max'
            }).reset_index()
            leaderboard.columns = ['NRP', 'Nilai Tertinggi', 'Last Submission']
            leaderboard = leaderboard.sort_values(
                ['Nilai Tertinggi', 'Last Submission'],
                ascending=[False, True]
            ).reset_index(drop=True)
            leaderboard.index += 1

            st.dataframe(
                leaderboard,
                use_container_width=True
            )
            
            st.divider()
            
            st.subheader("⚠️ Mahasiswa yang Perlu Perhatian")
            
            need_help = metrics['student_stats'][
                (metrics['student_stats']['passed'] == False) & 
                (metrics['student_stats']['attempts'] >= 3)
            ]
            
            if len(need_help) > 0:
                st.warning(f"⚠️ Ada {len(need_help)} mahasiswa dengan 3+ attempt tapi belum lulus")
                st.dataframe(need_help[['NRP', 'attempts', 'max_score']], use_container_width=True, hide_index=True)
            else:
                st.success("✅ Tidak ada mahasiswa yang perlu perhatian khusus")
        
        # PAGE: ANALISIS PERFORMA
        elif page == "Analisis Performa":
            st.header("👤 Analisis Performa Mahasiswa")
            
            student_list = sorted(df['NRP'].unique())
            selected_student = st.selectbox("Pilih Mahasiswa:", student_list)
            
            student_df = df[df['NRP'] == selected_student].sort_values('Date')
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Attempt", len(student_df))
            
            with col2:
                st.metric("Nilai Tertinggi", student_df['Nilai'].max())
            
            with col3:
                st.metric("Nilai Rata-rata", f"{student_df['Nilai'].mean():.1f}")
            
            with col4:
                passed = (student_df['Status'] == 'Lulus').any()
                st.metric("Status", "✅ Lulus" if passed else "❌ Belum Lulus")
            
            st.divider()
            
            st.plotly_chart(plot_score_progress(df, selected_student), use_container_width=True)
            
            st.divider()
            
            col1, col2 = st.columns([2, 1])
            
            with col1:
                st.subheader("📝 Riwayat Submission")
                display_df = student_df[['Date', 'Nilai', 'Status']].copy()
                display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d %H:%M:%S')
                st.dataframe(display_df, use_container_width=True, hide_index=True)
            
            with col2:
                st.subheader("📊 Statistik")
                
                if len(student_df) > 1:
                    first_score = student_df['Nilai'].iloc[0]
                    last_score = student_df['Nilai'].iloc[-1]
                    improvement = last_score - first_score
                    
                    st.metric("Peningkatan", f"{improvement:+.0f}", 
                             delta=f"{improvement:+.0f} poin")
                
                if len(student_df) > 1:
                    time_diffs = student_df['Date'].diff().dt.total_seconds() / 3600
                    avg_time = time_diffs.mean()
                    st.metric("Rata-rata Jeda", f"{avg_time:.1f} jam")
                
                if passed:
                    first_pass_idx = student_df[student_df['Status'] == 'Lulus'].index[0]
                    attempt_to_pass = list(student_df.index).index(first_pass_idx) + 1
                    st.metric("Lulus di Attempt ke-", attempt_to_pass)
        
        # PAGE: PATTERN SUBMISSION
        elif page == "Pattern Submission":
            st.header("📊 Pattern & Analisis Waktu Submission")
            
            st.subheader("🔥 Heatmap Waktu Submission")
            st.plotly_chart(plot_submission_heatmap(df.copy()), use_container_width=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.subheader("⏰ Jam Tersibuk")
                hourly = df.groupby(df['Date'].dt.hour).size().reset_index()
                hourly.columns = ['Hour', 'Count']
                hourly = hourly.sort_values('Count', ascending=False).head(5)
                
                fig = px.bar(hourly, x='Hour', y='Count', 
                           title='Top 5 Jam Tersibuk',
                           color='Count',
                           color_continuous_scale='Blues')
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.subheader("📅 Hari Tersibuk")
                daily = df.groupby(df['Date'].dt.day_name()).size().reset_index()
                daily.columns = ['Day', 'Count']
                
                day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 
                           'Friday', 'Saturday', 'Sunday']
                daily['Day'] = pd.Categorical(daily['Day'], categories=day_order, ordered=True)
                daily = daily.sort_values('Day')
                
                fig = px.bar(daily, x='Day', y='Count',
                           title='Submission per Hari',
                           color='Count',
                           color_continuous_scale='Greens')
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            st.subheader("🎯 Analisis Jumlah Attempt")
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.plotly_chart(plot_attempts_before_pass(df), use_container_width=True)
            
            with col2:
                df['attempt_number'] = df.groupby('NRP').cumcount() + 1
                success_by_attempt = df.groupby('attempt_number').agg({
                    'Status': lambda x: (x == 'Lulus').sum() / len(x) * 100
                }).reset_index()
                success_by_attempt.columns = ['Attempt', 'Success Rate']
                
                fig = px.line(success_by_attempt, x='Attempt', y='Success Rate',
                            title='Success Rate per Attempt',
                            markers=True)
                st.plotly_chart(fig, use_container_width=True)
        
        # PAGE: DASHBOARD DOSEN
        elif page == "Dashboard Dosen":
            st.header("👨‍🏫 Dashboard Pengajar")
            
            st.subheader("📊 Overview Kelas")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Mahasiswa", metrics['unique_students'])
            
            with col2:
                st.metric(
                    "Sudah Lulus",
                    metrics['students_passed'],
                    delta=f"{metrics['students_passed']/metrics['unique_students']*100:.0f}%"
                )
            
            with col3:
                st.metric("Belum Lulus", metrics['students_not_passed'])
            
            with col4:
                st.metric("Avg Attempt/Student", f"{metrics['avg_attempts']:.1f}")
            
            st.divider()
            
            st.plotly_chart(plot_pass_rate_by_student(df), use_container_width=True)
            
            st.divider()
            
            st.subheader("📈 Trend Performa Kelas")
            
            daily_stats = df.groupby(df['Date'].dt.date).agg({
                'Status': lambda x: (x == 'Lulus').sum() / len(x) * 100,
                'Nilai': 'mean'
            }).reset_index()
            daily_stats.columns = ['Date', 'Pass Rate', 'Avg Score']
            
            fig = make_subplots(specs=[[{"secondary_y": True}]])
            
            fig.add_trace(
                go.Scatter(x=daily_stats['Date'], y=daily_stats['Pass Rate'],
                          name='Pass Rate', line=dict(color='green')),
                secondary_y=False
            )
            
            fig.add_trace(
                go.Scatter(x=daily_stats['Date'], y=daily_stats['Avg Score'],
                          name='Avg Score', line=dict(color='blue')),
                secondary_y=True
            )
            
            fig.update_layout(title='Trend Harian: Pass Rate & Rata-rata Nilai')
            fig.update_xaxes(title_text='Tanggal')
            fig.update_yaxes(title_text='Pass Rate (%)', secondary_y=False)
            fig.update_yaxes(title_text='Rata-rata Nilai', secondary_y=True)
            
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            st.subheader("📋 Detail Semua Mahasiswa")
            
            student_detail = metrics['student_stats'].copy()
            student_detail['Status'] = student_detail['passed'].apply(
                lambda x: '✅ Lulus' if x else '❌ Belum Lulus'
            )
            student_detail = student_detail.sort_values('max_score', ascending=False)
            
            st.dataframe(
                student_detail[['NRP', 'attempts', 'avg_score', 'max_score', 'Status']],
                use_container_width=True,
                hide_index=True
            )
        
        # PAGE: PREDICTIVE ANALYTICS
        elif page == "Predictive Analytics":
            st.header("🔮 Predictive Analytics")
            
            st.info("📊 Analisis prediktif menggunakan pattern dari data historis")
            
            st.subheader("📈 Probabilitas Kelulusan per Mahasiswa")
            
            predictions = []
            for nrp in df['NRP'].unique():
                prob = predict_pass_probability(df, nrp)
                student_data = df[df['NRP'] == nrp]
                passed = (student_data['Status'] == 'Lulus').any()
                
                predictions.append({
                    'NRP': nrp,
                    'Probability': prob,
                    'Attempts': len(student_data),
                    'Max Score': student_data['Nilai'].max(),
                    'Status': '✅ Lulus' if passed else '❌ Belum Lulus'
                })
            
            pred_df = pd.DataFrame(predictions)
            pred_df = pred_df.sort_values('Probability', ascending=False)
            
            def get_risk_color(prob):
                if prob >= 70:
                    return '🟢 Low Risk'
                elif prob >= 40:
                    return '🟡 Medium Risk'
                else:
                    return '🔴 High Risk'
            
            pred_df['Risk Category'] = pred_df['Probability'].apply(get_risk_color)
            
            fig = px.bar(
                pred_df,
                x='NRP',
                y='Probability',
                color='Risk Category',
                title='Prediksi Probabilitas Kelulusan',
                color_discrete_map={
                    '🟢 Low Risk': '#28a745',
                    '🟡 Medium Risk': '#ffc107',
                    '🔴 High Risk': '#dc3545'
                }
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            st.subheader("📋 Detail Prediksi")
            
            filter_option = st.radio(
                "Filter:",
                ["Semua", "High Risk Only", "Belum Lulus Only"]
            )
            
            filtered_pred = pred_df.copy()
            if filter_option == "High Risk Only":
                filtered_pred = filtered_pred[filtered_pred['Risk Category'] == '🔴 High Risk']
            elif filter_option == "Belum Lulus Only":
                filtered_pred = filtered_pred[filtered_pred['Status'] == '❌ Belum Lulus']
            
            st.dataframe(filtered_pred, use_container_width=True, hide_index=True)
            
            st.divider()
            
            st.subheader("📈 Prediksi Nilai Next Attempt")
            
            selected_student = st.selectbox(
                "Pilih mahasiswa untuk prediksi:",
                pred_df['NRP'].tolist()
            )
            
            student_history = df[df['NRP'] == selected_student].sort_values('Date')
            
            if len(student_history) >= 2:
                scores = student_history['Nilai'].values
                attempts = np.arange(len(scores))
                
                z = np.polyfit(attempts, scores, 1)
                p = np.poly1d(z)
                
                next_attempt = len(scores)
                predicted_score = p(next_attempt)
                predicted_score = max(0, min(100, predicted_score))
                
                col1, col2 = st.columns(2)
                
                with col1:
                    st.metric(
                        "Prediksi Nilai Next Attempt",
                        f"{predicted_score:.0f}",
                        delta=f"{predicted_score - scores[-1]:+.0f} dari attempt terakhir"
                    )
                    
                    if predicted_score >= 60:
                        st.success("✅ Diprediksi akan lulus di attempt berikutnya!")
                    else:
                        st.warning("⚠️ Mungkin perlu attempt tambahan")
                
                with col2:
                    fig = go.Figure()
                    
                    fig.add_trace(go.Scatter(
                        x=attempts + 1,
                        y=scores,
                        mode='markers',
                        name='Actual',
                        marker=dict(size=10, color='blue')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=np.arange(0, next_attempt + 2),
                        y=p(np.arange(0, next_attempt + 2)),
                        mode='lines',
                        name='Trend',
                        line=dict(dash='dash', color='gray')
                    ))
                    
                    fig.add_trace(go.Scatter(
                        x=[next_attempt + 1],
                        y=[predicted_score],
                        mode='markers',
                        name='Predicted',
                        marker=dict(size=15, color='red', symbol='star')
                    ))
                    
                    fig.update_layout(
                        title=f'Prediksi untuk {selected_student}',
                        xaxis_title='Attempt',
                        yaxis_title='Nilai'
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("ℹ️ Tidak cukup data untuk membuat prediksi (minimal 2 attempt)")
        
        # PAGE: CUSTOM ANALYTICS
        elif page == "Custom Analytics":
            st.header("📊 Custom Analytics & Export")
            
            st.info("💡 Buat analisis custom dan export data sesuai kebutuhan")
            
            st.subheader("🔍 Custom Filters")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                status_filter = st.multiselect(
                    "Status:",
                    options=df['Status'].unique(),
                    default=df['Status'].unique()
                )
            
            with col2:
                min_score = st.number_input("Nilai Minimum:", 0, 100, 0)
                max_score = st.number_input("Nilai Maximum:", 0, 100, 100)
            
            with col3:
                date_range = st.date_input(
                    "Rentang Tanggal:",
                    value=(df['Date'].min(), df['Date'].max())
                )
            
            filtered_df = df[
                (df['Status'].isin(status_filter)) &
                (df['Nilai'] >= min_score) &
                (df['Nilai'] <= max_score)
            ]
            
            if len(date_range) == 2:
                filtered_df = filtered_df[
                    (filtered_df['Date'].dt.date >= date_range[0]) &
                    (filtered_df['Date'].dt.date <= date_range[1])
                ]
            
            st.success(f"✅ {len(filtered_df)} records setelah filtering")
            
            st.divider()
            
            st.subheader("📊 Custom Visualizations")
            
            viz_type = st.selectbox(
                "Pilih Tipe Visualisasi:",
                ["Score Distribution", "Timeline", "Box Plot", "Scatter Plot", "Correlation"]
            )
            
            if viz_type == "Score Distribution":
                fig = px.histogram(filtered_df, x='Nilai', nbins=20, 
                                 title='Distribusi Nilai (Filtered)')
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Timeline":
                timeline_data = filtered_df.groupby(filtered_df['Date'].dt.date).size().reset_index()
                timeline_data.columns = ['Date', 'Count']
                fig = px.line(timeline_data, x='Date', y='Count', 
                            title='Timeline Submission (Filtered)', markers=True)
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Box Plot":
                fig = px.box(filtered_df, x='Status', y='Nilai', 
                           title='Box Plot Nilai per Status (Filtered)')
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Scatter Plot":
                filtered_df['Attempt Number'] = filtered_df.groupby('NRP').cumcount() + 1
                fig = px.scatter(filtered_df, x='Attempt Number', y='Nilai', 
                               color='Status', title='Scatter: Attempt vs Nilai (Filtered)')
                st.plotly_chart(fig, use_container_width=True)
            
            elif viz_type == "Correlation":
                corr_df = filtered_df.copy()
                corr_df['Hour'] = corr_df['Date'].dt.hour
                corr_df['DayOfWeek'] = corr_df['Date'].dt.dayofweek
                
                numeric_cols = ['Nilai', 'Hour', 'DayOfWeek']
                corr_matrix = corr_df[numeric_cols].corr()
                
                fig = px.imshow(corr_matrix, 
                              title='Correlation Matrix',
                              labels=dict(color="Correlation"),
                              color_continuous_scale='RdBu')
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            st.subheader("📥 Export Data")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                csv = filtered_df.to_csv(index=False)
                st.download_button(
                    label="📄 Download Filtered Data (CSV)",
                    data=csv,
                    file_name=f"filtered_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col2:
                summary = metrics['student_stats'].to_csv(index=False)
                st.download_button(
                    label="📊 Download Summary Stats (CSV)",
                    data=summary,
                    file_name=f"summary_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            with col3:
                full_csv = df.to_csv(index=False)
                st.download_button(
                    label="💾 Download Full Dataset (CSV)",
                    data=full_csv,
                    file_name=f"full_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            
            st.divider()
            
            st.subheader("📋 Filtered Data Preview")
            st.dataframe(filtered_df, use_container_width=True)
            
            st.subheader("📈 Statistics (Filtered Data)")
            
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Records", len(filtered_df))
            
            with col2:
                st.metric("Unique Students", filtered_df['NRP'].nunique())
            
            with col3:
                st.metric("Avg Score", f"{filtered_df['Nilai'].mean():.1f}")
            
            with col4:
                pass_rate = (filtered_df['Status'] == 'Lulus').sum() / len(filtered_df) * 100 if len(filtered_df) > 0 else 0
                st.metric("Pass Rate", f"{pass_rate:.1f}%")
        
        # PAGE: COMPARE ASSIGNMENTS
        elif page == "Compare Assignments":
            st.header("🔄 Compare Assignments")
            
            if len(selected_assignments) < 2:
                st.warning("⚠️ Pilih minimal 2 assignments di sidebar untuk membandingkan")
                st.stop()
            
            st.info(f"📊 Membandingkan {len(selected_assignments)} assignments")
            
            st.subheader("📊 Perbandingan Metrics")
            
            comparison_data = []
            for assignment_name, assignment_df in all_data.items():
                metrics_temp = calculate_metrics(assignment_df)
                comparison_data.append({
                    'Assignment': assignment_name,
                    'Total Submissions': metrics_temp['total_submissions'],
                    'Unique Students': metrics_temp['unique_students'],
                    'Pass Rate (%)': round(metrics_temp['pass_rate'], 1),
                    'Avg Score': round(metrics_temp['avg_score'], 1),
                    'Avg Attempts': round(metrics_temp['avg_attempts'], 1),
                    'Students Passed': metrics_temp['students_passed'],
                    'Students Not Passed': metrics_temp['students_not_passed']
                })
            
            comparison_df = pd.DataFrame(comparison_data)
            
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            col1, col2 = st.columns(2)
            
            with col1:
                fig = px.bar(
                    comparison_df,
                    x='Assignment',
                    y='Pass Rate (%)',
                    title='Pass Rate per Assignment',
                    color='Pass Rate (%)',
                    color_continuous_scale='RdYlGn'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                fig = px.bar(
                    comparison_df,
                    x='Assignment',
                    y='Avg Score',
                    title='Rata-rata Nilai per Assignment',
                    color='Avg Score',
                    color_continuous_scale='Blues'
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            st.subheader("👥 Performa Mahasiswa Across Assignments")
            
            all_students = set()
            for df_temp in all_data.values():
                all_students.update(df_temp['NRP'].unique())
            
            student_comparison = []
            for nrp in all_students:
                student_row = {'NRP': nrp}
                for assignment_name, assignment_df in all_data.items():
                    student_data = assignment_df[assignment_df['NRP'] == nrp]
                    if len(student_data) > 0:
                        max_score = student_data['Nilai'].max()
                        passed = (student_data['Status'] == 'Lulus').any()
                        student_row[f"{assignment_name} - Score"] = max_score
                        student_row[f"{assignment_name} - Status"] = '✅' if passed else '❌'
                    else:
                        student_row[f"{assignment_name} - Score"] = '-'
                        student_row[f"{assignment_name} - Status"] = '-'
                
                student_comparison.append(student_row)
            
            student_comparison_df = pd.DataFrame(student_comparison)
            
            status_cols = [col for col in student_comparison_df.columns if 'Status' in col]
            student_comparison_df['Total Passed'] = student_comparison_df[status_cols].apply(
                lambda row: sum(1 for x in row if x == '✅'),
                axis=1
            )
            
            student_comparison_df = student_comparison_df.sort_values('Total Passed', ascending=False)
            
            st.dataframe(student_comparison_df, use_container_width=True, hide_index=True)
            
            st.divider()
            
            st.subheader("📈 Analisis Kesulitan Assignment")
            
            difficulty_metrics = []
            for assignment_name, assignment_df in all_data.items():
                metrics_temp = calculate_metrics(assignment_df)
                
                difficulty_score = (100 - metrics_temp['pass_rate']) + (metrics_temp['avg_attempts'] * 10)
                
                difficulty_metrics.append({
                    'Assignment': assignment_name,
                    'Difficulty Score': round(difficulty_score, 1),
                    'Pass Rate': round(metrics_temp['pass_rate'], 1),
                    'Avg Attempts': round(metrics_temp['avg_attempts'], 1),
                    'Avg Score': round(metrics_temp['avg_score'], 1)
                })
            
            difficulty_df = pd.DataFrame(difficulty_metrics)
            difficulty_df = difficulty_df.sort_values('Difficulty Score', ascending=False)
            
            def get_difficulty_label(score):
                if score >= 80:
                    return '🔴 Very Hard'
                elif score >= 60:
                    return '🟠 Hard'
                elif score >= 40:
                    return '🟡 Medium'
                else:
                    return '🟢 Easy'
            
            difficulty_df['Difficulty Level'] = difficulty_df['Difficulty Score'].apply(get_difficulty_label)
            
            col1, col2 = st.columns([1, 1])
            
            with col1:
                st.dataframe(difficulty_df, use_container_width=True, hide_index=True)
            
            with col2:
                fig = px.bar(
                    difficulty_df,
                    x='Assignment',
                    y='Difficulty Score',
                    color='Difficulty Level',
                    title='Difficulty Score per Assignment',
                    color_discrete_map={
                        '🔴 Very Hard': '#dc3545',
                        '🟠 Hard': '#fd7e14',
                        '🟡 Medium': '#ffc107',
                        '🟢 Easy': '#28a745'
                    }
                )
                fig.update_layout(xaxis_tickangle=-45)
                st.plotly_chart(fig, use_container_width=True)
            
            st.divider()
            
            st.subheader("📊 Distribusi Nilai Comparison")
            
            combined_for_dist = combine_dataframes(all_data)
            
            fig = px.box(
                combined_for_dist,
                x='Assignment',
                y='Nilai',
                color='Assignment',
                title='Box Plot Nilai per Assignment'
            )
            fig.update_layout(xaxis_tickangle=-45, showlegend=False)
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.error("❌ Data tidak dapat dimuat atau kosong")
        st.info("Pastikan Google Sheets URL benar dan kamu punya akses ke sheet tersebut")

else:
    st.info("ℹ️ Pilih assignment di sidebar untuk memulai")
    
    with st.expander("📚 Available Assignments"):
        for assignment_name in SHEETS_CONFIG.keys():
            st.markdown(f"- **{assignment_name}**")