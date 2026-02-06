"""
FastAPI Dashboard untuk WhatsApp Bot Control
- Start/Stop bot
- View status real-time
- WebSocket log streaming
- Barcode generator
"""

from fastapi import FastAPI, WebSocket, UploadFile, File, Form, HTTPException
from fastapi.responses import FileResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import os
from pathlib import Path
import threading
import time

from bot_manager import bot_manager, LOG_FILE_PATH
from barcode_generator import barcode_generator

# Initialize FastAPI app
app = FastAPI(title="WhatsApp Bot Dashboard", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve uploads (mount dulu sebelum static)
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Serve generated barcodes
generated_dir = Path("generated_barcodes")
generated_dir.mkdir(exist_ok=True)
app.mount("/generated_barcodes", StaticFiles(directory="generated_barcodes"), name="generated_barcodes")

# Serve static files (mount terakhir)
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Thread untuk auto-check restart
def background_restart_checker():
    """Background thread untuk check dan auto-restart bot kalau perlu"""
    while True:
        try:
            bot_manager.check_and_restart_if_needed()
        except Exception as e:
            print(f"Error di restart checker: {e}")
        time.sleep(5)

restart_thread = threading.Thread(target=background_restart_checker, daemon=True)
restart_thread.start()


# ============ REST ENDPOINTS ============

@app.get("/")
async def root():
    """Serve dashboard HTML"""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file, media_type="text/html")
    else:
        return {"error": "Dashboard file not found", "path": str(html_file.absolute())}

@app.get("/dashboard")
async def dashboard_page():
    """Alternative dashboard endpoint"""
    html_file = Path("static/index.html")
    if html_file.exists():
        return FileResponse(html_file, media_type="text/html")
    else:
        return {"error": "Dashboard file not found"}

@app.post("/api/bot/start")
async def start_bot():
    """Start bot process"""
    result = bot_manager.start()
    return result

@app.post("/api/bot/stop")
async def stop_bot():
    """Stop bot process"""
    result = bot_manager.stop()
    return result

@app.get("/api/bot/status")
async def get_status():
    """Get current bot status"""
    status = bot_manager.get_status()
    return status

@app.get("/api/bot/log")
async def get_log():
    """Get recent logs"""
    logs = bot_manager.get_log_realtime()
    return {"logs": logs}

@app.get("/api/bot/last-number")
async def get_last_number():
    """Get nomor terakhir terkirim"""
    last_number = bot_manager.get_last_sent_number(LOG_FILE_PATH)
    return {
        "last_number": last_number,
        "timestamp": time.time()
    }

@app.post("/api/barcode/generate")
async def generate_barcode(
    place_id: str = Form(...),
    filename: str = Form(None),
    logo: UploadFile = File(None)
):
    """Generate barcode dengan optional logo"""
    
    logo_path = None
    
    # Handle logo upload
    if logo:
        try:
            # Save logo temporary
            logo_path = f"uploads/{logo.filename}"
            with open(logo_path, "wb") as f:
                content = await logo.read()
                f.write(content)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Gagal upload logo: {str(e)}")
    
    # Generate barcode
    result = barcode_generator.generate(
        place_id=place_id,
        output_filename=filename,
        logo_path=logo_path
    )
    
    # Clean up uploaded logo
    if logo_path and os.path.exists(logo_path):
        try:
            os.remove(logo_path)
        except:
            pass
    
    return result

@app.get("/api/barcode/list")
async def list_barcodes():
    """List semua barcode yang sudah dibuat"""
    barcodes = barcode_generator.list_barcodes()
    return {"barcodes": barcodes}

@app.delete("/api/barcode/{filename}")
async def delete_barcode(filename: str):
    """Delete barcode"""
    result = barcode_generator.delete_barcode(filename)
    return result

@app.get("/api/data")
async def get_dashboard_data():
    """Get all dashboard data in one call"""
    status = bot_manager.get_status()
    last_number = bot_manager.get_last_sent_number(LOG_FILE_PATH)
    barcodes = barcode_generator.list_barcodes()
    
    return {
        "status": status,
        "last_number": last_number,
        "barcodes": barcodes
    }


# ============ WEBSOCKET ENDPOINTS ============

@app.websocket("/ws/logs")
async def websocket_logs(websocket: WebSocket):
    """WebSocket untuk realtime log streaming"""
    await websocket.accept()
    
    try:
        while True:
            # Get new logs
            logs = bot_manager.get_log_realtime()
            
            if logs:
                for log in logs:
                    await websocket.send_json({"type": "log", "data": log})
            
            # Check status every second
            status = bot_manager.get_status()
            await websocket.send_json({"type": "status", "data": status})
            
            await asyncio.sleep(1)
    
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        await websocket.close()


# ============ HEALTH CHECK ============

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "timestamp": time.time()
    }


if __name__ == "__main__":
    import uvicorn
    
    # Run server
    # Untuk production dengan ngrok: uvicorn app:app --host 0.0.0.0 --port 8000
    print("\n" + "="*60)
    print("🚀 FastAPI Dashboard Starting...")
    print("📍 Local: http://127.0.0.1:8000")
    print("🌐 With ngrok: ngrok http 8000")
    print("="*60 + "\n")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )
