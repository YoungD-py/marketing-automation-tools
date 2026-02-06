"""
Barcode Generator Module
- Generate QR code dari place_id
- Optional: Overlay dengan logo customer
- Save dengan custom filename
"""

import qrcode
from PIL import Image
import os
from datetime import datetime

class BarcodeGenerator:
    def __init__(self, output_dir="generated_barcodes"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def generate(self, place_id, output_filename=None, logo_path=None):
        """
        Generate QR code dengan optional logo overlay
        
        Args:
            place_id: Google Maps place ID
            output_filename: Nama file output (default: auto-generated)
            logo_path: Path ke logo image (optional)
        
        Returns:
            dict: {status, message, file_path, url}
        """
        try:
            # Generate QR dari place_id
            data_link = f"https://search.google.com/local/writereview?placeid={place_id}"
            
            # Create QR code
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction untuk logo overlay
                box_size=10,
                border=4,
            )
            qr.add_data(data_link)
            qr.make(fit=True)
            
            # Convert to image
            qr_img = qr.make_image(fill_color="black", back_color="white")
            
            # Overlay logo kalau ada
            if logo_path and os.path.exists(logo_path):
                qr_img = self._overlay_logo(qr_img, logo_path)
            
            # Generate filename kalau tidak disediakan
            if not output_filename:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_filename = f"barcode_{timestamp}.png"
            
            # Ensure .png extension
            if not output_filename.endswith('.png'):
                output_filename += '.png'
            
            # Save file
            file_path = os.path.join(self.output_dir, output_filename)
            qr_img.save(file_path)
            
            return {
                "status": "success",
                "message": "Barcode berhasil dibuat",
                "file_path": file_path,
                "filename": output_filename,
                "place_id": place_id,
                "url": f"/generated_barcodes/{output_filename}"
            }
        
        except Exception as e:
            return {
                "status": "error",
                "message": f"Gagal generate barcode: {str(e)}"
            }
    
    def _overlay_logo(self, qr_img, logo_path):
        """
        Overlay logo di tengah QR code
        """
        try:
            # Open logo
            logo = Image.open(logo_path)
            
            # Resize logo ke 25% dari QR code
            qr_width, qr_height = qr_img.size
            logo_size = qr_width // 4
            logo = logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
            
            # Kalau logo ada alpha, extract
            if logo.mode == 'RGBA':
                logo_bg = Image.new('RGB', logo.size, 'white')
                logo_bg.paste(logo, mask=logo.split()[3])
                logo = logo_bg
            elif logo.mode != 'RGB':
                logo = logo.convert('RGB')
            
            # Paste logo di tengah QR
            logo_pos = ((qr_width - logo_size) // 2, (qr_height - logo_size) // 2)
            qr_img.paste(logo, logo_pos)
            
            return qr_img
        
        except Exception as e:
            print(f"Warning: Gagal overlay logo: {str(e)}")
            return qr_img  # Return QR tanpa logo
    
    def delete_barcode(self, filename):
        """Delete barcode file"""
        try:
            file_path = os.path.join(self.output_dir, filename)
            if os.path.exists(file_path):
                os.remove(file_path)
                return {"status": "success", "message": "Barcode dihapus"}
            else:
                return {"status": "error", "message": "File tidak ditemukan"}
        except Exception as e:
            return {"status": "error", "message": f"Gagal hapus: {str(e)}"}
    
    def list_barcodes(self):
        """List semua barcode yang sudah dibuat"""
        try:
            files = []
            if os.path.exists(self.output_dir):
                for f in os.listdir(self.output_dir):
                    if f.endswith('.png'):
                        file_path = os.path.join(self.output_dir, f)
                        file_size = os.path.getsize(file_path)
                        files.append({
                            "filename": f,
                            "url": f"/generated_barcodes/{f}",
                            "size": file_size
                        })
            return files
        except Exception as e:
            return []


# Global instance
barcode_generator = BarcodeGenerator("generated_barcodes")
