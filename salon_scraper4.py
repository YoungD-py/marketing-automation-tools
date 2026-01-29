from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager
import time

# === PENGATURAN ===
KATA_KUNCI = "SALON BITUNG"  # Ganti sesuai kebutuhan
JEDA_SCROLL = 2  # Detik jeda setiap scroll

# --- FUNGSI BARU UNTUK FORMAT NOMOR TELEPON ---
def format_nomor_telepon(nomor_mentah):
    """
    Fungsi ini membersihkan dan memformat nomor telepon ke format 62.
    Contoh: '0812-3456-7890' menjadi '6281234567890'
             '(0771) 20479' menjadi '6277120479'
    """
    if not nomor_mentah or nomor_mentah == "Tidak ada nomor":
        return None

    # 1. Hapus semua karakter selain angka
    nomor_bersih = ''.join(filter(str.isdigit, nomor_mentah))

    # 2. Jika nomor dimulai dengan '0', ganti dengan '62'
    if nomor_bersih.startswith('0'):
        return '62' + nomor_bersih[1:]
    # 3. Jika sudah dimulai dengan '62', biarkan saja
    elif nomor_bersih.startswith('62'):
        return nomor_bersih
    # 4. Jika formatnya aneh dan tidak dimulai dengan 0 atau 62, abaikan saja
    else:
        # Anda bisa menambahkan logika lain di sini jika ada format lain
        # Untuk saat ini, kita anggap tidak valid jika tidak diawali 0
        return None
# --- AKHIR FUNGSI BARU ---


# Setup Chrome
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Buka Google Maps
driver.get("https://www.google.com/maps")
time.sleep(3)

# Cari kata kunci
search_box = driver.find_element(By.ID, "searchboxinput")
search_box.send_keys(KATA_KUNCI)
search_box.send_keys(Keys.ENTER)
time.sleep(5)

# Scroll semua hasil
try:
    scrollable_div = driver.find_element(By.XPATH, '//div[@role="feed"]')
    last_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)

    while True:
        driver.execute_script("arguments[0].scrollTo(0, arguments[0].scrollHeight)", scrollable_div)
        time.sleep(JEDA_SCROLL)
        new_height = driver.execute_script("return arguments[0].scrollHeight", scrollable_div)
        if new_height == last_height:
            break
        last_height = new_height
    print("✅ Semua hasil sudah dimuat. Mengambil data...")
except Exception as e:
    print(f"Tidak dapat menemukan panel hasil untuk di-scroll, mungkin hanya ada sedikit hasil. Lanjut mengambil data. Error: {e}")


# Ambil semua link sebagai teks, bukan elemen
place_links = list(set([p.get_attribute("href") for p in driver.find_elements(By.XPATH, '//a[contains(@href, "google.com/maps/place/")]')]))
print(f"🔍 Ditemukan {len(place_links)} link tempat unik.")

hasil = []
for link in place_links:
    try:
        driver.get(link)
        time.sleep(3)
        
        # Kita tidak perlu nama lagi untuk output, tapi biarkan saja jika ada error
        try:
            nama = driver.find_element(By.XPATH, '//h1').text
        except:
            nama = "Tidak ada nama"
        
        try:
            telp_button = driver.find_element(By.XPATH, '//button[contains(@aria-label, "Telepon") or contains(@aria-label, "Phone") or contains(@aria-label, "Call")]')
            telp_mentah = telp_button.get_attribute("aria-label").replace("Telepon: ", "").replace("Call: ", "").replace("Phone: ", "")
        except:
            telp_mentah = "Tidak ada nomor"

        # --- MODIFIKASI LOGIKA INTI DIMULAI DI SINI ---
        
        nomor_terformat = format_nomor_telepon(telp_mentah)
        
        # Hanya tambahkan ke hasil jika nomornya valid dan berhasil diformat
        if nomor_terformat:
            if nomor_terformat not in hasil: # Mencegah duplikat nomor
                 hasil.append(nomor_terformat)
                 print(nomor_terformat) # Cetak langsung format yang benar
            
        # --- MODIFIKASI LOGIKA INTI SELESAI ---
    
    except Exception as e:
        print(f"❌ Error saat memproses link {link}: {e}")

driver.quit()

# --- MODIFIKASI BAGIAN PENYIMPANAN FILE ---
with open("hasil_salon_BITUNG.txt", "w", encoding="utf-8") as f:
    for nomor in hasil:
        f.write(nomor + "\n")

print(f"\n✅ Selesai! {len(hasil)} nomor telepon unik tersimpan di hasil_salon_BITUNG.txt")