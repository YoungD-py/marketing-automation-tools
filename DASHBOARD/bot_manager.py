"""
Bot Manager - Handle background service untuk WhatsApp bot
- Start/Stop bot process
- Auto-restart dengan limit counter
- Track status dan log realtime
"""

import subprocess
import threading
import time
import os
from pathlib import Path
from datetime import datetime
from queue import Queue

class BotManager:
    def __init__(self, script_path):
        self.script_path = script_path
        self.process = None
        self.is_running = False
        self.restart_count = 0
        self.max_restarts = 5  # Limit auto-restart
        self.restart_cooldown = 10  # 10 detik antara restart
        self.log_queue = Queue()  # Queue untuk streaming log
        self.last_restart_time = 0
        
    def start(self):
        """Mulai bot process"""
        if self.is_running:
            return {"status": "error", "message": "Bot sudah berjalan"}
        
        try:
            # Cek script ada atau tidak
            if not os.path.exists(self.script_path):
                return {"status": "error", "message": f"Script tidak ditemukan: {self.script_path}"}
            
            # Get script directory (CHAT BOT WA folder)
            script_dir = os.path.dirname(os.path.abspath(self.script_path))
            
            # Start process dengan working directory ke script_dir
            # Supaya barcode.jpg dan nomor.txt bisa ditemukan
            self.process = subprocess.Popen(
                ["python", self.script_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
                encoding='utf-8',
                cwd=script_dir,  # Set working directory
                env={**os.environ, 'PYTHONIOENCODING': 'utf-8'}
            )
            
            self.is_running = True
            self.restart_count = 0
            
            # Thread untuk read output realtime
            threading.Thread(target=self._read_output, daemon=True).start()
            
            return {
                "status": "success",
                "message": "Bot dimulai",
                "pid": self.process.pid,
                "working_dir": script_dir
            }
        except Exception as e:
            self.is_running = False
            return {"status": "error", "message": f"Gagal start bot: {str(e)}"}
    
    def stop(self):
        """Stop bot process dengan force kill Chrome driver + bot process"""
        if not self.is_running or self.process is None:
            return {"status": "error", "message": "Bot tidak berjalan"}
        
        try:
            pid = self.process.pid
            
            # Kill Chrome processes yang mungkin still running
            import subprocess as sp
            try:
                # Force kill semua Chrome process yang related
                sp.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                       stdout=sp.DEVNULL, stderr=sp.DEVNULL)
                sp.run(["taskkill", "/F", "/IM", "chromedriver.exe"], 
                       stdout=sp.DEVNULL, stderr=sp.DEVNULL)
            except:
                pass
            
            # Kill bot process
            try:
                # Try graceful terminate dulu
                self.process.terminate()
                try:
                    self.process.wait(timeout=3)
                    msg = "Bot dihentikan gracefully"
                except subprocess.TimeoutExpired:
                    # Kalau masih hidup, force kill
                    self.process.kill()
                    self.process.wait()
                    msg = "Bot dipaksa dihentikan (SIGKILL)"
            except:
                pass
            
            self.is_running = False
            self.restart_count = 0
            
            return {"status": "success", "message": f"{msg} + Chrome killed"}
        except Exception as e:
            self.is_running = False
            self.restart_count = 0
            return {"status": "error", "message": f"Error stop bot: {str(e)}"}
    
    def get_status(self):
        """Get current bot status"""
        if self.process and self.process.poll() is not None:
            # Process sudah mati tapi flag masih running
            self.is_running = False
        
        return {
            "running": self.is_running,
            "pid": self.process.pid if self.process else None,
            "restart_count": self.restart_count,
            "max_restarts": self.max_restarts,
            "timestamp": datetime.now().isoformat()
        }
    
    def _read_output(self):
        """Read process output realtime dan push ke queue"""
        try:
            if not self.process or not self.process.stdout:
                self.log_queue.put("[ERROR] Process stdout tidak tersedia")
                return
            
            while self.is_running and self.process:
                try:
                    line = self.process.stdout.readline()
                    if line:
                        timestamp = datetime.now().strftime("%H:%M:%S")
                        log_entry = f"[{timestamp}] {line.rstrip()}"
                        self.log_queue.put(log_entry)
                        # Print juga ke console untuk debug
                        print(log_entry, flush=True)
                    else:
                        # Cek apakah process masih jalan
                        if self.process.poll() is not None:
                            # Process sudah exit
                            self.is_running = False
                            break
                        time.sleep(0.1)
                except Exception as e:
                    print(f"[ERROR] Read error: {str(e)}", flush=True)
                    time.sleep(0.1)
                    
        except Exception as e:
            msg = f"[ERROR] Output reader crash: {str(e)}"
            self.log_queue.put(msg)
            print(msg, flush=True)
        finally:
            self.is_running = False
    
    def get_log_realtime(self):
        """Get log dari queue (untuk WebSocket)"""
        logs = []
        while not self.log_queue.empty():
            try:
                logs.append(self.log_queue.get_nowait())
            except:
                break
        return logs
    
    def get_last_sent_number(self, log_file_path):
        """Baca nomor terakhir dari log_terkirim.txt"""
        try:
            if not os.path.exists(log_file_path):
                return None
            
            with open(log_file_path, 'r') as f:
                lines = f.readlines()
                if lines:
                    last_line = lines[-1].strip()
                    return last_line
            return None
        except Exception as e:
            return f"Error: {str(e)}"
    
    def check_and_restart_if_needed(self):
        """Auto-restart jika process mati dengan limit"""
        if self.is_running:
            if self.process and self.process.poll() is not None:
                # Process mati
                self.is_running = False
                
                # Check apakah bisa restart
                time_since_last_restart = time.time() - self.last_restart_time
                
                if self.restart_count < self.max_restarts and time_since_last_restart > self.restart_cooldown:
                    self.restart_count += 1
                    self.last_restart_time = time.time()
                    
                    print(f"[AUTO-RESTART] Attempt {self.restart_count}/{self.max_restarts}")
                    self.log_queue.put(f"[AUTO-RESTART] Attempt {self.restart_count}/{self.max_restarts}")
                    
                    result = self.start()
                    return result
                elif self.restart_count >= self.max_restarts:
                    msg = f"Max restart limit ({self.max_restarts}) tercapai. Berhenti auto-restart."
                    self.log_queue.put(msg)
                    return {"status": "error", "message": msg}


# Global bot manager instance
BOT_SCRIPT_PATH = r"D:\DAMARA PROJECT\CHAT BOT WA\script.py"
LOG_FILE_PATH = r"D:\DAMARA PROJECT\CHAT BOT WA\log_terkirim.txt"

bot_manager = BotManager(BOT_SCRIPT_PATH)
