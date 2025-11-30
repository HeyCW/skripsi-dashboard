# ⚡ Quick Setup untuk Streamlit Cloud

## Error: "could not locate runnable browser"?
Ini karena OAuth **tidak bisa** jalan di Streamlit Cloud. Kamu harus pakai **Service Account**.

---

## 🚀 Setup 5 Menit

### 1️⃣ Buat Service Account (2 menit)

1. Buka [Google Cloud Console](https://console.cloud.google.com/iam-admin/serviceaccounts?project=sheets-connection-471408)
2. Klik **+ CREATE SERVICE ACCOUNT**
3. Isi nama: `streamlit-dashboard`
4. Klik **CREATE AND CONTINUE** → **CONTINUE** → **DONE**

### 2️⃣ Download Key (30 detik)

1. Klik service account yang baru dibuat
2. Tab **KEYS** → **ADD KEY** → **Create new key**
3. Pilih **JSON** → **CREATE**
4. File JSON akan terdownload

### 3️⃣ Copy ke Streamlit Secrets (1 menit)

1. Buka file JSON yang didownload dengan text editor
2. Akan terlihat seperti ini:
   ```json
   {
     "type": "service_account",
     "project_id": "sheets-connection-471408",
     "private_key_id": "abc123...",
     "private_key": "-----BEGIN PRIVATE KEY-----\n...",
     "client_email": "streamlit-dashboard@sheets-connection-471408.iam.gserviceaccount.com",
     ...
   }
   ```

3. Buka **Streamlit Cloud Dashboard** → App kamu → **Settings** → **Secrets**

4. Paste dalam format TOML (convert dari JSON):
   ```toml
   [gcp_service_account]
   type = "service_account"
   project_id = "sheets-connection-471408"
   private_key_id = "isi dari file JSON"
   private_key = "-----BEGIN PRIVATE KEY-----\nMIIEvQI...\n-----END PRIVATE KEY-----\n"
   client_email = "streamlit-dashboard@sheets-connection-471408.iam.gserviceaccount.com"
   client_id = "123456789..."
   auth_uri = "https://accounts.google.com/o/oauth2/auth"
   token_uri = "https://oauth2.googleapis.com/token"
   auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
   client_x509_cert_url = "https://www.googleapis.com/robot/v1/metadata/x509/..."
   universe_domain = "googleapis.com"
   ```

   ⚠️ **PENTING**:
   - `private_key` harus dalam **satu baris**
   - Gunakan `\n` untuk line breaks (jangan enter)
   - Semua value pakai tanda kutip `"`

5. Klik **Save**

### 4️⃣ Share Google Sheets (1 menit)

1. Copy **service account email** dari file JSON (contoh: `streamlit-dashboard@sheets-connection-471408.iam.gserviceaccount.com`)

2. Buka **SETIAP** Google Sheets:
   - Redis List/Set
   - Redis Timeseries
   - MongoDB
   - Neo4J
   - Big Data Assignment 1
   - Big Data Assignment 2
   - Big Data Assignment 3

3. Untuk setiap sheet:
   - Klik **Share**
   - Paste service account email
   - Set permission: **Viewer**
   - Klik **Send**

### 5️⃣ Enable API (30 detik)

1. Buka [Google Sheets API](https://console.cloud.google.com/apis/library/sheets.googleapis.com?project=sheets-connection-471408)
2. Klik **ENABLE**

---

## ✅ Done!

Restart app di Streamlit Cloud dan klik **Connect to Google Sheets**.

Seharusnya langsung connect tanpa error!

---

## 🆘 Masih Error?

### Error: "Permission denied"
→ **Solusi:** Sheet belum dishare ke service account email

### Error: "API not enabled"
→ **Solusi:** Enable Google Sheets API (step 5)

### Error: "Invalid private_key"
→ **Solusi:** Format private_key salah. Pastikan:
   - Satu baris
   - Pakai `\n` untuk line breaks
   - Ada kutip `"` di awal dan akhir

### Error lain?
→ Buka **Debug panel** di app untuk lihat detail error

---

## 💡 Tips

- Service account email format: `nama@project-id.iam.gserviceaccount.com`
- Cek debug panel untuk verifikasi service account terdeteksi
- Pastikan **semua 7 sheets** sudah dishare
- Private key harus include `-----BEGIN PRIVATE KEY-----` dan `-----END PRIVATE KEY-----`

---

**Need more detail?** → Read full guide: [STREAMLIT_CLOUD_SETUP.md](STREAMLIT_CLOUD_SETUP.md)
