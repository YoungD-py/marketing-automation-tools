import qrcode
from PIL import Image

# === LINK TUJUAN QR CODE ===
data = "https://search.google.com/local/writereview?placeid=ChIJs8kvWI2D5i0Rs1vTY4dnJNI"

# === BUAT QR CODE OBJECT ===
qr = qrcode.QRCode(
    version=1,
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(data)
qr.make(fit=True)

# === BIKIN QR DENGAN WARNA NORMAL TANPA GRADASI ===
img = qr.make_image(
    fill_color=(0, 43, 91),        # Warna QR
    back_color=(255, 255, 255)     # Background putih
).convert('RGBA')

# === TAMBAH LOGO DI TENGAH ===
logo = Image.open("bengkel.jpg")  # Ganti nama file kalau perlu
logo_size = 80
logo = logo.resize((logo_size, logo_size))

pos = (
    (img.size[0] - logo.size[0]) // 2,
    (img.size[1] - logo.size[1]) // 2
)
img.paste(logo, pos)

# === SIMPAN HASIL QR CODE ===
img.save("bengkel1.png")
print("✅ QR CODE WARNA BIASA SUDAH DIBUAT!")
