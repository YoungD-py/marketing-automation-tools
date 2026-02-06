import qrcode
import os 

place_id = "ChIJ--UaaUuN2TER7DyAFdPg0go"
nama_file_output = "style.png"
direktori_penyimpanan = os.path.dirname(os.path.abspath(__file__))
path_lengkap_output = os.path.join(direktori_penyimpanan, nama_file_output)

data_link = f"https://search.google.com/local/writereview?placeid={place_id}"
img = qrcode.make(data_link)
img.save(path_lengkap_output)

print(f"✅ Berhasil! QR Code telah dibuat dan disimpan di lokasi:\n{path_lengkap_output}")

