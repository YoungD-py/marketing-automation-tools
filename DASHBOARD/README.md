# 🎛️ WhatsApp Bot Dashboard

Control & monitor WhatsApp bot dari mana saja via ngrok!

## 📋 Fitur

✅ **Start/Stop Bot** - Control bot dari dashboard  
✅ **Status Monitor** - Live status dengan auto-refresh  
✅ **Log Realtime** - WebSocket streaming log  
✅ **Nomor Terakhir** - Cek nomor terakhir terkirim  
✅ **Auto-Restart** - Bot otomatis restart (dengan limit)  
✅ **Barcode Generator** - Generate QR code + logo overlay  
✅ **Responsive Design** - Mobile-friendly dashboard  

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd D:\DAMARA PROJECT\DASHBOARD
pip install -r requirements.txt
```

### 2. Run Dashboard

```bash
python app.py
```

Server akan berjalan di: `http://127.0.0.1:8000`

### 3. Setup ngrok (Untuk Remote Access)

**Install ngrok:**
```bash
# Windows (via Chocolatey)
choco install ngrok

# Atau download dari: https://ngrok.com/download
```

**Run ngrok tunnel:**
```bash
ngrok http 8000
```

Output akan menunjukkan URL seperti:
```
https://xxxx-xx-xxx-xxx-xx.ngrok.io
```

Akses dashboard via URL tersebut dari browser manapun! 🌐

---

## 📁 Folder Structure

```
DASHBOARD/
├── app.py                    # FastAPI main app
├── bot_manager.py           # Bot subprocess manager
├── barcode_generator.py     # QR code generator
├── requirements.txt         # Python dependencies
├── static/
│   └── index.html          # Dashboard frontend
├── uploads/                # Temp logo uploads
├── generated_barcodes/     # Generated QR codes
└── README.md
```

---

## 🎮 Dashboard Features

### Bot Control Panel
- **START** - Jalankan bot (subprocess)
- **STOP** - Hentikan bot
- **Status Display** - Running/Stopped status
- **Process ID** - PID bot process
- **Restart Count** - Track auto-restart attempts (max: 5)

### Log Viewer
- Real-time log streaming via WebSocket
- Color-coded log levels (Error/Success/Warning)
- Auto-scroll to latest
- Max 500 entries untuk performa

### Last Sent Number
- Baca dari `log_terkirim.txt`
- Auto-update setiap 10 detik
- Format: `62XXXXXXXXXX`

### Barcode Generator
**Input Manual:**
- Place ID: Google Maps place ID
- Filename: Custom output filename (optional)
- Logo: Upload logo customer (optional, PNG/JPG)

**Output:**
- Generate QR code dengan Google Maps review link
- Optional logo overlay di tengah QR
- Auto-list di "Barcode List"
- Download/delete functionality

---

## 🔧 Configuration

### Bot Manager Config (bot_manager.py)

```python
BOT_SCRIPT_PATH = r"D:\DAMARA PROJECT\CHAT BOT WA\script.py"
LOG_FILE_PATH = r"D:\DAMARA PROJECT\CHAT BOT WA\log_terkirim.txt"

# Auto-restart settings
max_restarts = 5           # Max auto-restart attempts
restart_cooldown = 10      # Detik antara restart attempts
```

### API Endpoints

```
POST   /api/bot/start                    # Start bot
POST   /api/bot/stop                     # Stop bot
GET    /api/bot/status                   # Get status
GET    /api/bot/log                      # Get recent logs
GET    /api/bot/last-number              # Get last sent number
POST   /api/barcode/generate             # Generate barcode
GET    /api/barcode/list                 # List barcodes
DELETE /api/barcode/{filename}           # Delete barcode
GET    /api/dashboard                    # Get all data

WS     /ws/logs                          # WebSocket log streaming
```

---

## 🌐 Ngrok Hosting Setup

### Step-by-step:

1. **Get ngrok auth token** (free account di ngrok.com):
   ```bash
   ngrok config add-authtoken YOUR_TOKEN_HERE
   ```

2. **Run dashboard** (terminal 1):
   ```bash
   cd D:\DAMARA PROJECT\DASHBOARD
   python app.py
   ```

3. **Run ngrok** (terminal 2):
   ```bash
   ngrok http 8000
   ```

4. **Access Dashboard**:
   - Buka browser: `https://xxxx-ngrok-url.ngrok.io`
   - Bookmark untuk akses cepat

### Keep PC Running:
- Jangan shutdown PC (kalau server di rumah)
- Atau setup Windows Task Scheduler untuk auto-start

---

## 📝 Log File Handling

**Location**: `D:\DAMARA PROJECT\CHAT BOT WA\log_terkirim.txt`

Format:
```
62812345678901
62818765432109
62821234567890
```

Dashboard membaca file ini untuk show "Last Sent Number".

---

## 🎨 Barcode Features

### Generate QR Code:
1. Input Place ID dari Google Maps
2. (Optional) Upload logo customer
3. (Optional) Custom filename
4. Click "Generate Barcode"

### Features:
- QR code encode: Google Maps review link
- Logo overlay: Centered, 25% size
- High error correction (untuk logo tidak mengrusak QR)
- Auto-list di folder: `/generated_barcodes/`

### Download:
- Click barcode di "Barcode List" untuk preview
- Download button untuk simpan ke PC

---

## 🐛 Troubleshooting

### Bot tidak start
- Check: Apakah `script.py` ada di path?
- Check: Apakah python + dependencies installed?
- Check: Apakah file `nomor.txt` ada?

### WebSocket log tidak streaming
- Check: Browser console (F12)
- Try: Refresh page
- Try: Restart dashboard

### Ngrok connection timeout
- Check: Internet connection
- Check: Firewall/antivirus block?
- Try: `ngrok tcp 8000` (alternative)

### Barcode tidak generate
- Check: Filename sudah ada? (akan overwrite)
- Check: Logo format PNG/JPG?
- Check: Place ID valid?

---

## 📦 Dependency Info

```
fastapi       - Web framework
uvicorn       - ASGI server
python-multipart - Form data handling
qrcode        - QR code generation
pillow        - Image processing (logo overlay)
```

---

## 🔐 Security Notes

⚠️ **PENTING untuk Production:**
- Ngrok URL bersifat public - siapa saja bisa akses
- Tambahkan authentication/password jika perlu
- Use VPN/private network untuk lebih aman
- Disable F12 console di production

---

## 💡 Tips

✅ Bookmark ngrok URL buat akses cepat  
✅ Buat profile di ngrok buat static subdomain (paid)  
✅ Auto-restart handle crash, tapi monitor tetap  
✅ Log viewer delete auto 500 entries (garbage collection)  
✅ Kalau PC mati, bot juga mati - setup auto-restart di Windows  

---

## 📞 Support

Kalau ada error, check:
1. Terminal output (stdout/stderr)
2. Browser console (F12)
3. Log viewer di dashboard
4. File: `log_terkirim.txt` (untuk bot output)

---

**Happy Automating! 🚀**
