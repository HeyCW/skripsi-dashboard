# 📊 Dashboard Analitik Mahasiswa

Dashboard interaktif untuk menganalisis performa mahasiswa berdasarkan data submission dari Google Sheets.

## ✨ Features

### 📈 Analytics Pages
1. **Overview** - Metrics utama dan visualisasi distribusi nilai
2. **Submission History** - Timeline dan leaderboard submission
3. **Analisis Performa** - Detail progress per mahasiswa
4. **Pattern Submission** - Heatmap waktu submission
5. **Dashboard Dosen** - View untuk pengajar
6. **Predictive Analytics** - Prediksi kelulusan mahasiswa
7. **Custom Analytics** - Filter custom dan export data
8. **Compare Assignments** - Bandingkan multiple assignments

### 🎯 Key Metrics
- Total submissions
- Pass rate
- Rata-rata nilai
- Student attempts distribution
- Submission patterns (by hour/day)

### 📊 Visualizations
- Score distribution histograms
- Timeline charts
- Pass rate by student
- Submission heatmaps
- Progress tracking
- Difficulty analysis

## 🚀 Quick Start

### Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Setup credentials:**

   Buat file `.streamlit/secrets.toml`:
   ```toml
   [oauth]
   client_id = "your-client-id"
   project_id = "your-project-id"
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_secret = "your-client-secret"
   redirect_uris = ["http://localhost"]
   ```

3. **Run:**
   ```bash
   streamlit run dashboard.py
   ```

### Streamlit Cloud Deployment

Untuk deploy ke Streamlit Cloud, **gunakan Service Account** (bukan OAuth).

📖 **Baca panduan lengkap:** [STREAMLIT_CLOUD_SETUP.md](STREAMLIT_CLOUD_SETUP.md)

## 📁 Project Structure

```
skripsi-dashboard/
├── .streamlit/
│   └── secrets.toml           # Credentials config (gitignored)
├── credentials/
│   └── token.pickle           # OAuth token cache (gitignored)
├── dashboard.py               # Main application
├── requirements.txt           # Python dependencies
├── README.md                  # This file
├── STREAMLIT_CLOUD_SETUP.md  # Cloud deployment guide
└── .gitignore
```

## 🔐 Authentication Methods

Dashboard ini support **2 metode authentication**:

### 1. OAuth (untuk Local Development)
- Menggunakan OAuth 2.0 flow
- User login via browser
- Token disimpan di `credentials/token.pickle`

### 2. Service Account (untuk Streamlit Cloud)
- Tidak perlu browser interaction
- Langsung authorized via JSON key
- **Wajib share Google Sheets ke service account email**

## 📊 Google Sheets Configuration

Dashboard terhubung ke 7 Google Sheets assignments:

1. Redis List/Set
2. Redis Timeseries
3. MongoDB
4. Neo4J
5. Big Data Assignment 1
6. Big Data Assignment 2
7. Big Data Assignment 3

Setiap sheet harus memiliki kolom:
- `NRP` - Nomor mahasiswa
- `Date` - Tanggal submission
- `Nilai` - Score (0-100)
- `Status` - "Lulus" atau "Tidak Lulus"

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Visualization:** Plotly
- **Data Processing:** Pandas, NumPy
- **Google Sheets API:** gspread, google-auth
- **Authentication:** OAuth 2.0 / Service Account

## 📦 Dependencies

```
streamlit
pandas
numpy
gspread
google-auth
google-auth-oauthlib
google-auth-httplib2
plotly
```

Install semua dengan:
```bash
pip install -r requirements.txt
```

## 🎨 Features Detail

### Multi-Assignment Support
- Pilih satu atau multiple assignments
- View mode: Individual atau Combined
- Cross-assignment comparison

### Predictive Analytics
- Linear regression untuk prediksi nilai
- Pass probability calculation
- Risk categorization (Low/Medium/High)

### Custom Filters
- Filter by status, score range, date range
- Multiple visualization options
- Export filtered data to CSV

### Real-time Data
- Auto-refresh every 5 minutes (cache)
- Manual refresh button
- Live submission tracking

## 🔧 Troubleshooting

### "Permission denied" error
- Pastikan Google Sheets dishare ke email kamu (OAuth) atau service account email

### "API not enabled"
- Enable Google Sheets API di Google Cloud Console

### Token expired
- Hapus file `credentials/token.pickle`
- Login ulang

### Streamlit Cloud tidak bisa login
- Jangan pakai OAuth di cloud
- Pakai Service Account (lihat [STREAMLIT_CLOUD_SETUP.md](STREAMLIT_CLOUD_SETUP.md))

## 📝 License

This project is for educational purposes.

## 👨‍💻 Author

Charles - Skripsi Dashboard Project

## 🙏 Acknowledgments

- Streamlit team untuk amazing framework
- Google untuk Sheets API
- Plotly untuk visualization library

---

**Happy Analyzing! 📊**
