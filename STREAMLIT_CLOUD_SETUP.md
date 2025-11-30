# 🚀 Setup Dashboard di Streamlit Cloud

## Kenapa Perlu Service Account?

OAuth dengan `run_local_server()` **TIDAK BISA** dipakai di Streamlit Cloud karena tidak ada browser lokal untuk authorize. Solusinya: **Service Account**.

---

## 📋 Step-by-Step Setup Service Account

### 1. Buat Service Account di Google Cloud Console

1. Buka [Google Cloud Console](https://console.cloud.google.com)
2. Pilih project: `sheets-connection-471408`
3. Navigate ke: **IAM & Admin** → **Service Accounts**
4. Klik **+ CREATE SERVICE ACCOUNT**
5. Isi:
   - **Service account name**: `streamlit-dashboard` (atau nama lain)
   - **Description**: `Service account for Streamlit dashboard`
6. Klik **CREATE AND CONTINUE**
7. **Grant this service account access** → Skip (klik CONTINUE)
8. **Grant users access** → Skip (klik DONE)

### 2. Create & Download Key

1. Klik service account yang baru dibuat
2. Tab **KEYS** → **ADD KEY** → **Create new key**
3. Pilih **JSON** → **CREATE**
4. File JSON akan terdownload otomatis

### 3. Enable Google Sheets API

1. Di Google Cloud Console, ke **APIs & Services** → **Library**
2. Cari "Google Sheets API"
3. Klik **ENABLE**

### 4. Share Google Sheets ke Service Account

**INI PENTING!** Service account butuh akses ke sheets.

1. Buka file JSON yang didownload
2. Copy email service account (contoh: `streamlit-dashboard@sheets-connection-471408.iam.gserviceaccount.com`)
3. Buka **setiap Google Sheets** yang mau diakses
4. Klik **Share** button
5. Paste email service account
6. Set permission: **Viewer**
7. Klik **Send**

Ulangi untuk semua sheets:
- Redis List/Set
- Redis Timeseries
- MongoDB
- Neo4J
- Big Data Assignment 1
- Big Data Assignment 2
- Big Data Assignment 3

### 5. Configure Streamlit Cloud Secrets

1. Buka dashboard Streamlit Cloud
2. Pilih app kamu
3. Klik **Settings** → **Secrets**
4. Copy isi file JSON service account
5. Paste dalam format TOML:

```toml
[gcp_service_account]
type = "service_account"
project_id = "sheets-connection-471408"
private_key_id = "abc123..."
private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAAS...\n-----END PRIVATE KEY-----\n"
client_email = "streamlit-dashboard@sheets-connection-471408.iam.gserviceaccount.com"
client_id = "123456789"
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
universe_domain = "googleapis.com"
```

⚠️ **PENTING:**
- `private_key` harus dalam satu baris dengan `\n` untuk line breaks
- Pastikan ada `\n` di awal dan akhir private key
- Semua value string pakai tanda kutip `"`

6. Klik **Save**

### 6. Deploy!

App akan auto-restart dan langsung connect menggunakan service account.

---

## 🔧 Troubleshooting

### Error: "Permission denied"
- **Penyebab:** Service account belum dishare ke Google Sheets
- **Solusi:** Share sheets ke service account email

### Error: "API not enabled"
- **Penyebab:** Google Sheets API belum dienable
- **Solusi:** Enable Google Sheets API di GCP Console

### Error: "Invalid private_key"
- **Penyebab:** Format private_key salah di secrets.toml
- **Solusi:** Pastikan private_key dalam satu baris dengan `\n` sebagai line separator

### App stuck loading
- **Penyebab:** Secrets tidak terkonfigurasi dengan benar
- **Solusi:** Cek format TOML di Streamlit Cloud secrets, restart app

---

## 📚 Referensi

- [Streamlit Secrets Management](https://docs.streamlit.io/streamlit-community-cloud/deploy-your-app/secrets-management)
- [Google Service Accounts](https://cloud.google.com/iam/docs/service-accounts)
- [gspread with Service Account](https://docs.gspread.org/en/latest/oauth2.html#service-account)

---

## ✅ Checklist

- [ ] Service account dibuat
- [ ] JSON key didownload
- [ ] Google Sheets API enabled
- [ ] Semua 7 sheets dishare ke service account email
- [ ] Secrets dikonfigurasi di Streamlit Cloud
- [ ] App deployed dan berjalan

---

**Selamat! Dashboard kamu sekarang bisa jalan di Streamlit Cloud! 🎉**
