from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import random

# === PENGATURAN ===
PROVINSI = "JAWA TIMUR"  # Ganti sesuai provinsi kamu
KATA_KUNCI_LIST = [
"VAPESTORE KOTA SURABAYA",
"VAPE SHOP KOTA SURABAYA",

"VAPESTORE KOTA MALANG",
"VAPE SHOP KOTA MALANG",

"VAPESTORE KOTA BATU",
"VAPE SHOP KOTA BATU",

"VAPESTORE KOTA BLITAR",
"VAPE SHOP KOTA BLITAR",

"VAPESTORE KOTA KEDIRI",
"VAPE SHOP KOTA KEDIRI",

"VAPESTORE KOTA MADIUN",
"VAPE SHOP KOTA MADIUN",

"VAPESTORE KOTA MOJOKERTO",
"VAPE SHOP KOTA MOJOKERTO",

"VAPESTORE KOTA PASURUAN",
"VAPE SHOP KOTA PASURUAN",

"VAPESTORE KOTA PROBOLINGGO",
"VAPE SHOP KOTA PROBOLINGGO",

"VAPESTORE KABUPATEN SIDOARJO",
"VAPE SHOP KABUPATEN SIDOARJO",

"VAPESTORE KABUPATEN GRESIK",
"VAPE SHOP KABUPATEN GRESIK",

"VAPESTORE KABUPATEN JEMBER",
"VAPE SHOP KABUPATEN JEMBER",

"VAPESTORE KABUPATEN MALANG",
"VAPE SHOP KABUPATEN MALANG",

"VAPESTORE KABUPATEN KEDIRI",
"VAPE SHOP KABUPATEN KEDIRI",

"VAPESTORE KABUPATEN MOJOKERTO",
"VAPE SHOP KABUPATEN MOJOKERTO",

"VAPESTORE KABUPATEN PASURUAN",
"VAPE SHOP KABUPATEN PASURUAN",

"VAPESTORE KABUPATEN PROBOLINGGO",
"VAPE SHOP KABUPATEN PROBOLINGGO",

"VAPESTORE KABUPATEN BANYUWANGI",
"VAPE SHOP KABUPATEN BANYUWANGI",

"VAPESTORE KABUPATEN BLITAR",
"VAPE SHOP KABUPATEN BLITAR",

"VAPESTORE KABUPATEN MADIUN",
"VAPE SHOP KABUPATEN MADIUN",

"VAPESTORE KABUPATEN NGANJUK",
"VAPE SHOP KABUPATEN NGANJUK",

"VAPESTORE KABUPATEN LUMAJANG",
"VAPE SHOP KABUPATEN LUMAJANG",

"VAPESTORE KABUPATEN BONDOWOSO",
"VAPE SHOP KABUPATEN BONDOWOSO",

"VAPESTORE KABUPATEN SITUBONDO",
"VAPE SHOP KABUPATEN SITUBONDO",

"VAPESTORE KABUPATEN JOMBANG",
"VAPE SHOP KABUPATEN JOMBANG",

"VAPESTORE KABUPATEN TULUNGAGUNG",
"VAPE SHOP KABUPATEN TULUNGAGUNG",

"VAPESTORE KABUPATEN PACITAN",
"VAPE SHOP KABUPATEN PACITAN",

"VAPESTORE KABUPATEN TUBAN",
"VAPE SHOP KABUPATEN TUBAN",

"VAPESTORE KABUPATEN BOJONEGORO",
"VAPE SHOP KABUPATEN BOJONEGORO",

"VAPESTORE KABUPATEN LAMONGAN",
"VAPE SHOP KABUPATEN LAMONGAN",

"VAPESTORE KABUPATEN MAGETAN",
"VAPE SHOP KABUPATEN MAGETAN",

"VAPESTORE KABUPATEN NGAWI",
"VAPE SHOP KABUPATEN NGAWI",

"VAPESTORE KABUPATEN PONOROGO",
"VAPE SHOP KABUPATEN PONOROGO",

"VAPESTORE KABUPATEN TRENGGALEK",
"VAPE SHOP KABUPATEN TRENGGALEK",

"VAPESTORE KABUPATEN BANGKALAN",
"VAPE SHOP KABUPATEN BANGKALAN",

"VAPESTORE KABUPATEN SAMPANG",
"VAPE SHOP KABUPATEN SAMPANG",

"VAPESTORE KABUPATEN PAMEKASAN",
"VAPE SHOP KABUPATEN PAMEKASAN",

"VAPESTORE KABUPATEN SUMENEP",
"VAPE SHOP KABUPATEN SUMENEP"

]  # Tambah atau kurangi sesuai kebutuhan
JEDA_SCROLL = 2  # Detik jeda setiap scroll

# === SET GLOBAL UNTUK NOMOR UNIK ===
semua_nomor_unik = set()  # Simpan nomor yang sudah pernah ditemukan (duplikat di skip)

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


for kata_kunci in KATA_KUNCI_LIST:
    print(f"\n🔍 Memulai scraping untuk: {kata_kunci}")
    print("="*50)
    
    # Setup Chrome untuk setiap kata kunci
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-blink-features=AutomationControlled")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

    # Buka Google Maps
    driver.get("https://www.google.com/maps")
    time.sleep(5)
    
    # Handle popup consent kalau ada
    try:
        reject_btn = driver.find_element(By.XPATH, "//button[contains(., 'Reject') or contains(., 'Tolak')]")
        reject_btn.click()
        time.sleep(2)
    except:
        pass
    
    # Tunggu search box muncul (coba beberapa selector berbeda)
    search_box = None
    selectors = [
        (By.ID, "searchboxinput"),
        (By.NAME, "q"),
        (By.CSS_SELECTOR, "input[aria-label*='Search']"),
        (By.CSS_SELECTOR, "input[placeholder*='Search']"),
        (By.XPATH, "//input[@id='searchboxinput']"),
        (By.XPATH, "//input[contains(@aria-label, 'Search')]")
    ]
    
    for by, value in selectors:
        try:
            search_box = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((by, value))
            )
            print(f"✅ Search box ditemukan dengan: {by} = {value}")
            break
        except:
            continue
    
    if not search_box:
        print(f"❌ Search box tidak ditemukan dengan semua selector. Skip kata kunci ini.")
        driver.save_screenshot(f"error_{kata_kunci.replace(' ', '_')}.png")
        driver.quit()
        continue

    # Cari kata kunci
    search_box.click()
    time.sleep(1)
    search_box.send_keys(kata_kunci)
    time.sleep(1)
    search_box.send_keys(Keys.ENTER)
    time.sleep(12)  # Tunggu lebih lama agar hasil load sempurna

    # Scroll semua hasil
    try:
        # Tunggu panel hasil muncul dulu
        scrollable_div = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, '//div[@role="feed"]'))
        )
        time.sleep(3)
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
        print(f"⚠️ Tidak dapat menemukan panel hasil untuk di-scroll, mungkin hanya ada sedikit hasil. Lanjut mengambil data. Error: {e}")
        time.sleep(3)


    # Ambil semua link sebagai teks, bukan elemen
    place_links = list(set([p.get_attribute("href") for p in driver.find_elements(By.XPATH, '//a[contains(@href, "google.com/maps/place/")]')]))
    print(f"🔍 Ditemukan {len(place_links)} link tempat unik.")

    hasil_temp = []  # Nomor dari keyword ini
    for idx, link in enumerate(place_links, 1):
        try:
            driver.get(link)
            time.sleep(random.uniform(3, 6))  # Jeda random 3-6 detik untuk terlihat natural
            
            # Tunggu halaman detail muncul
            try:
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//h1'))
                )
            except:
                pass
            
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

            # --- LOGIKA DUPLIKAT UNIK ---
            nomor_terformat = format_nomor_telepon(telp_mentah)
            
            # Hanya tambahkan jika nomornya valid dan BELUM PERNAH TERSIMPAN
            if nomor_terformat:
                if nomor_terformat not in semua_nomor_unik:  # Cek duplikat global
                    semua_nomor_unik.add(nomor_terformat)  # Tambah ke set global
                    hasil_temp.append(nomor_terformat)
                    print(f"✅ [{idx}/{len(place_links)}] {nomor_terformat}")
                else:
                    print(f"⏭️ [{idx}/{len(place_links)}] SKIP (duplikat): {nomor_terformat}")
                
        except ConnectionResetError as e:
            print(f"⚠️ [{idx}/{len(place_links)}] Connection reset, skip link ini dan lanjut... Error: {str(e)[:50]}")
            time.sleep(5)
            continue
        except Exception as e:
            print(f"❌ [{idx}/{len(place_links)}] Error: {str(e)[:60]}")

    print(f"📊 Dari keyword ini ditemukan {len(hasil_temp)} nomor unik baru.")
    driver.quit()
    
    if kata_kunci != KATA_KUNCI_LIST[-1]:  # Jika bukan kata kunci terakhir
        print("⏳ Menunggu 10 detik sebelum kata kunci berikutnya...")
        time.sleep(10)

# === SIMPAN SEMUA NOMOR UNIK KE 1 FILE ===
nama_file = f"hasil_vapestore_{PROVINSI.replace(' ', '_').lower()}.txt"
with open(nama_file, "w", encoding="utf-8") as f:
    for nomor in sorted(semua_nomor_unik):
        f.write(nomor + "\n")

print(f"\n🎉 SELESAI! Total {len(semua_nomor_unik)} nomor HP UNIK tersimpan di: {nama_file}")
