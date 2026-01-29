# VERSI 20.0 - THE UNBREAKABLE (DENGAN LOGIKA RETRY)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
import win32clipboard
from io import BytesIO
import time
import os
import random

# === PENGATURAN ===
FILE_NOMOR = "nomor.txt"
FILE_PROMOSI = "promosi.txt"
FILE_GAMBAR = "barcode.jpg"
FILE_LOG_TERKIRIM = "log_terkirim.txt"  # File untuk track nomor yang sudah terkirim

# === USER-AGENT LIST (Random untuk setiap session) ===
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
]

# === PROXY (Optional) - Set ke None jika tidak pakai proxy ===
# Format: "http://proxy-ip:port" atau "http://username:password@proxy-ip:port"
PROXY_LIST = [
    # "http://proxy1:8080",
    # "http://proxy2:8080",
    None  # Jika ingin tanpa proxy, biarkan None
]
PROXY_ENABLED = False  # Ubah ke True jika mau pakai proxy

# === JEDA ANTAR NOMOR (detik) ===
JEDA_MIN = 30  # Minimum jeda
JEDA_MAX = 60  # Maximum jeda

# === HELPER CLIPBOARD ===
def get_random_user_agent():
    """Return random user-agent dari list."""
    return random.choice(USER_AGENTS)


def get_random_proxy():
    """Return random proxy dari list (atau None jika tidak pakai proxy)."""
    if not PROXY_ENABLED:
        return None
    return random.choice(PROXY_LIST)


def type_like_human(element, text):
    """Ketik text dengan kecepatan human-like (random delay per karakter)."""
    for char in text:
        element.send_keys(char)
        # Jeda random 0.02-0.08 detik per karakter (balance: cepat tapi ga kedetect)
        time.sleep(random.uniform(0.02, 0.08))


def load_log_terkirim():
    """Load nomor yang sudah terkirim dari log file."""
    try:
        with open(FILE_LOG_TERKIRIM, "r", encoding="utf-8") as f:
            return set(line.strip() for line in f if line.strip())
    except FileNotFoundError:
        return set()


def save_to_log_terkirim(nomor):
    """Tambah nomor ke log terkirim."""
    try:
        with open(FILE_LOG_TERKIRIM, "a", encoding="utf-8") as f:
            f.write(nomor + "\n")
    except Exception as e:
        print(f"⚠️ Error save log: {e}")


def check_sudah_pernah_kirim(driver):
    """Check apakah sudah ada pesan outgoing (dari kita) di chat history."""
    try:
        time.sleep(2)  # Tunggu chat history load
        
        # Cari semua pesan yang ada di chat (outgoing message = right side)
        # Di WhatsApp Web, ciri pesan outgoing: memiliki class "message-out" atau data-testid tertentu
        outgoing_messages = driver.find_elements(By.XPATH, '//div[contains(@class, "message-out") or contains(@class, "msg-outgoing")]')
        
        if outgoing_messages:
            print(f"   ✅ TERDETEKSI {len(outgoing_messages)} PESAN OUTGOING DI CHAT INI!")
            print(f"   ⚠️ BERARTI SUDAH PERNAH DIKIRIM KE NOMOR INI! SKIP & JANGAN KIRIM LAGI...")
            return True
        else:
            print(f"   ✓ Tidak ada pesan sebelumnya, aman untuk kirim.")
            return False
            
    except Exception as e:
        print(f"   ⚠️ Error check chat history: {str(e)[:50]}")
        # Jika error, asumsikan belum pernah kirim (lanjut kirim)
        return False


def copy_image_to_clipboard(image_path):
    """Copy gambar ke clipboard Windows."""
    try:
        image = Image.open(image_path)
        output = BytesIO()
        image.save(output, 'BMP')
        data = output.getvalue()[14:]
        win32clipboard.OpenClipboard()
        win32clipboard.EmptyClipboard()
        win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
        win32clipboard.CloseClipboard()
        return True
    except Exception as e:
        print(f"❌ ERROR COPY GAMBAR KE CLIPBOARD: {e}")
        return False


def chunk_text(text, max_len=900):
    """Bagi teks jadi potongan <= max_len dengan menjaga kata utuh."""
    words = text.split()
    chunks = []
    current = []
    length = 0
    for w in words:
        # +1 untuk spasi jika bukan kata pertama
        add_len = len(w) + (1 if length > 0 else 0)
        if length + add_len > max_len:
            chunks.append(" ".join(current))
            current = [w]
            length = len(w)
        else:
            current.append(w)
            length += add_len
    if current:
        chunks.append(" ".join(current))
    return chunks

# === SETUP CHROME & DRIVER ===
chrome_options = Options()
chrome_options.add_argument("user-data-dir=" + os.path.join(os.getcwd(), "whatsapp_profile"))
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

# === RANDOM USER-AGENT ===
random_ua = get_random_user_agent()
chrome_options.add_argument(f"user-agent={random_ua}")
print(f"📱 User-Agent: {random_ua[:80]}...")

# === OPTIONAL PROXY ===
random_proxy = get_random_proxy()
if random_proxy:
    chrome_options.add_argument(f"--proxy-server={random_proxy}")
    print(f"🔄 Proxy: {random_proxy}")
else:
    print(f"🔄 Proxy: Disabled (menggunakan IP asli)")
gambar_path = os.path.abspath(FILE_GAMBAR)
if not os.path.exists(gambar_path):
    print(f"❌ ERROR: GAMBAR E ERROR COK '{FILE_GAMBAR}' GAK NEMU.")
    exit()
try:
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
except Exception as e:
    print(f"❌ CHROME E ERROR COK: {e}")
    exit()

# === MEMBACA FILE-FILE PENDUKUNG ===
try:
    with open(FILE_PROMOSI, "r", encoding="utf-8") as f:
        teks_promosi_dari_file = f.read()
    print(f"✅ TEKS E BENER '{FILE_PROMOSI}'")
except FileNotFoundError:
    print(f"❌ ERROR: TEKS E ERROR COK '{FILE_PROMOSI}' GAK NEMU!")
    driver.quit()
    exit()
try:
    with open(FILE_NOMOR, "r", encoding="utf-8") as f:
        nomor_list = [line.strip() for line in f if line.strip()]
    if not nomor_list:
        print("⚠️ FILE NOMOR E GAK ONOK COK.")
        driver.quit()
        exit()
except FileNotFoundError:
    print(f"❌ ERROR: File '{FILE_NOMOR}' GAK NEMU!")
    driver.quit()
    exit()

# === LOAD LOG NOMOR YANG SUDAH TERKIRIM ===
log_terkirim = load_log_terkirim()
print(f"📋 LOG TERKIRIM LOADED: {len(log_terkirim)} nomor sudah pernah dikirim")
nomor_list_filtered = [n for n in nomor_list if n not in log_terkirim]
print(f"📩 TOTAL NOMOR AKAN DIPROSES: {len(nomor_list_filtered)} (dari {len(nomor_list)} nomor)")

if not nomor_list_filtered:
    print("✅ SEMUA NOMOR SUDAH PERNAH TERKIRIM! TIDAK ADA YANG PERLU DIPROSES.")
    driver.quit()
    exit()

nomor_list = nomor_list_filtered  # Override dengan list yang sudah di-filter

# === LOGIN KE WHATSAPP WEB ===
driver.get("https://web.whatsapp.com")
print("✅ SCAN QR WA GAWE LOGIN...")
try:
    WebDriverWait(driver, 90).until(EC.presence_of_element_located((By.ID, 'pane-side')))
    print("✅ WhatsApp Web WES SIAP BOS.")
    print("⏳ NGENTENI FULL LOAD & SINKRON 45 DETIK...")
    time.sleep(45)
except TimeoutException:
    print("❌ Gagal MBUKAK halaman utama WhatsApp Web.")
    driver.quit()
    exit()

# === XPATH ===
XPATH_TOMBOL_LAMPIRKAN = '/html/body/div[1]/div/div/div/div/div[3]/div/div[5]/div/footer/div[1]/div/span/div/div/div/div[1]/div/span/button/div/div/div[1]/span'
XPATH_INPUT_GAMBAR = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
XPATH_KOTAK_CAPTION = '/html/body/div[1]/div/div/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[1]/div[3]/div/div/div[1]/div[1]/div[1]/p'
XPATH_TOMBOL_KIRIM_GAMBAR = '/html/body/div[1]/div/div/div/div/div[3]/div/div[3]/div[2]/div/span/div/div/div/div[2]/div/div[2]/div[2]/span/div/div/span'

# === PROSES UTAMA PENGIRIMAN PESAN ===
for nomor in nomor_list:
    # Convert 0XX -> 62XX (Indonesia format)
    if nomor.startswith("0"):
        nomor = "62" + nomor[1:]
    
    pesan_terkirim = False
    # --- LOGIKA RETRY ---
    for attempt in range(3): # PERCOBAAN 3X SETIAP NOMOR
        try:
            print(f"📩 PROSES NOMOR: {nomor} (Percobaan {attempt + 1})")
            url = f"https://web.whatsapp.com/send?phone={nomor}"
            driver.get(url)

            print("   - NGENTENI HALAMAN CHAT MBUKAK...")
            
            chat_terbuka = False
            waktu_mulai = time.time()
            waktu_maksimal = 60  # Tunggu 60 detik, kalau masih blank refresh
            refresh_done = False
            
            while time.time() - waktu_mulai < waktu_maksimal:
                try:
                    # Cek apakah tombol lampirkan sudah muncul (artinya chat berhasil terbuka)
                    driver.find_element(By.XPATH, XPATH_TOMBOL_LAMPIRKAN)
                    print("   - CHAT BERHASIL TERBUKA!")
                    chat_terbuka = True
                    break
                except:
                    # Cek apakah ada indikasi nomor tidak terdaftar/tidak aktif
                    try:
                        error_elements = driver.find_elements(By.XPATH, "//*[contains(text(), 'Phone number shared via url is invalid')]")
                        if error_elements:
                            print("   - NOMOR TIDAK VALID/TIDAK TERDAFTAR.")
                            break
                    except:
                        pass
                    
                    # Cek kalau layar blank >20 detik, refresh
                    if (time.time() - waktu_mulai) > 20 and not refresh_done:
                        try:
                            body_text = driver.execute_script("return document.body.innerText.length;")
                            if body_text < 20:
                                print("   - BLANK SCREEN TERDETEKSI, REFRESH...")
                                driver.refresh()
                                refresh_done = True
                        except:
                            pass
                    
                    time.sleep(2)
            
            if not chat_terbuka:
                if time.time() - waktu_mulai >= waktu_maksimal:
                    print("   - TIMEOUT: CHAT TIDAK TERBUKA SETELAH 60 DETIK")
                else:
                    print("   - NOMOR TIDAK VALID, SKIP KE NOMOR BERIKUTNYA")
                raise Exception("Chat tidak terbuka atau nomor tidak valid")

            # === CHECK APAKAH SUDAH PERNAH KIRIM KE NOMOR INI ===
            print("   - CHECKING CHAT HISTORY...")
            if check_sudah_pernah_kirim(driver):
                print(f"⏭️ SKIP NOMOR {nomor} (SUDAH PERNAH DIKIRIM)")
                raise Exception("Sudah pernah dikirim ke nomor ini (detected dari chat history)")
            
            # Klik kolom pesan input (XPATH message input yang user berikan)
            message_input = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div/div/div/div/div[3]/div/div[5]/div/footer/div[1]/div/span/div/div/div/div[3]/div[1]/p'))
            )
            message_input.click()
            print("   - NGEKLIK KOLOM PESAN...")
            time.sleep(1)

            # Copy gambar ke clipboard
            if not copy_image_to_clipboard(gambar_path):
                raise Exception("Gagal copy gambar ke clipboard")
            print("   - GAMBAR DICOPY KE CLIPBOARD...")
            time.sleep(1)

            # Paste gambar dengan Ctrl+V
            message_input.send_keys(Keys.CONTROL, 'v')
            print("   - GAMBAR DI-PASTE KE PESAN...")
            time.sleep(3)

            # Tunggu kolom caption preview muncul
            caption_preview = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.XPATH, XPATH_KOTAK_CAPTION))
            )
            print("   - PREVIEW GAMBAR MUNCUL, NGENTENI KOLOM CAPTION...")
            time.sleep(2)

            # Ketik caption di kolom caption preview dengan HUMAN-LIKE TYPING
            print("   - NGETIK CAPTION (HUMAN-LIKE SPEED)...")
            lines = teks_promosi_dari_file.split('\n')
            for idx, line in enumerate(lines):
                # Ketik karakter per karakter dengan random delay
                type_like_human(caption_preview, line)
                
                # Enter untuk line break (kecuali line terakhir)
                if idx < len(lines) - 1:
                    caption_preview.send_keys(Keys.SHIFT, Keys.ENTER)
                    time.sleep(random.uniform(0.1, 0.3))
            
            print("   - CAPTION KELAR DIKETIK.")
            time.sleep(2)

            # Klik tombol kirim
            WebDriverWait(driver, 20).until(
                EC.element_to_be_clickable((By.XPATH, XPATH_TOMBOL_KIRIM_GAMBAR))
            ).click()
            print("   - TOMBOL KIRIM DIKLIK...")

            print("   - NGENTENI KONFIRMASI PENGIRIMAN...")
            WebDriverWait(driver, 30).until(
                EC.invisibility_of_element_located((By.XPATH, XPATH_TOMBOL_KIRIM_GAMBAR))
            )
            time.sleep(15)
            
            # === SAVE KE LOG TERKIRIM ===
            save_to_log_terkirim(nomor)
            print(f"✅ Pesan ke {nomor} telah terkirim dengan sukses.")
            print(f"📋 Nomor ini sudah di-save ke log_terkirim.txt")
            pesan_terkirim = True
            break

        except StaleElementReferenceException:
            print(f"   - ❗️ TERDETEKSI KONTOL KONTOLAN NYOBA ULANG...")
            time.sleep(2)
            continue
        except Exception as e:
            print(f"❌ WA E GAK ONOK NOMOR E COK: {e}")
            break
    
    if not pesan_terkirim:
        print(f"⚠️ GAGAL KIRIM PESAN {nomor} SETELAH NGE TRY BERULANG.")
    else:
        # === JEDA PANJANG SEBELUM NOMOR BERIKUTNYA (untuk avoid detect) ===
        jeda_random = random.uniform(JEDA_MIN, JEDA_MAX)
        print(f"⏳ MENUNGGU {jeda_random:.1f} DETIK SEBELUM NOMOR BERIKUTNYA (UNTUK AVOID DETECT)...")
        time.sleep(jeda_random)

driver.quit()
print("\n\n SISTEM KELAR BOS BISA LU TINGGAL NGENTOTAN")
