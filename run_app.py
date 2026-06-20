#run_app.py
import subprocess, sys, time, socket
def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def main():
    print("====================================================")
    print("   AI Musteri Yorum Analiz Sistemi Baslatici")
    print("====================================================")

    # Check ports – if occupied, try to free them automatically
    import psutil
    def kill_port(port):
        """Terminate any process listening on the given port using psutil.
        Works on Windows; ignores AccessDenied / NoSuchProcess errors.
        """
        for proc in psutil.process_iter(['pid', 'name']):
            try:
                # Retrieve all inet connections for the process
                conns = proc.connections(kind='inet')
                for conn in conns:
                    if conn.laddr.port == port:
                        try:
                            proc.kill()
                            print(f"🛑 Killed PID {proc.pid} (port {port})")
                        except Exception as e:
                            print(f"⚠️ Failed to kill PID {proc.pid}: {e}")
                        return
            except (psutil.AccessDenied, psutil.NoSuchProcess, psutil.ZombieProcess):
                continue
        print(f"ℹ️ No process found using port {port}")
    if is_port_in_use(8000):
        print("[-] 8000 portu zaten kullanımda – temizleniyor...")
        kill_port(8000)
    if is_port_in_use(8501):
        print("[-] 8501 portu zaten kullanımda – temizleniyor...")
        kill_port(8501)

    print("[*] API Backend (FastAPI) baslatiliyor...")
    backend_cmd = [sys.executable, "-m", "uvicorn", "backend.app:app", "--host", "127.0.0.1", "--port", "8000"]
    backend_proc = subprocess.Popen(
        backend_cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    # Wait for backend to start up
    print("[*] Backend'in hazir olmasi bekleniyor (model yukleniyor)...")
    model_loaded = False
    for _ in range(45): # Wait up to 45 seconds for model download/load
        time.sleep(1)
        # Check health endpoint
        try:
            import requests
            resp = requests.get("http://127.0.0.1:8000/health", timeout=1)
            if resp.status_code == 200:
                data = resp.json()
                if data.get("model_loaded"):
                    print("[+] Backend ve DistilBERT modeli basariyla yuklendi!")
                    model_loaded = True
                    break
                else:
                    print("[*] Model yuklenmeye devam ediyor...")
        except Exception:
            pass

    if not model_loaded:
        print("[!] Uyari: Model yuklenmesi beklenenden uzun surdu. Streamlit baslatiliyor...")

    print("[*] Frontend (Streamlit) baslatiliyor...")
    frontend_cmd = [sys.executable, "-m", "streamlit", "run", "frontend/app.py", "--server.port", "8501"]
    frontend_proc = subprocess.Popen(frontend_cmd)

    print("\n[+] Uygulama basariyla baslatildi!")
    print(" -> Arayuze erismek icin tarayicinizda acin: http://localhost:8501")
    print(" -> Kapatmak icin: Ctrl+C tuslarina basin.\n")

    try:
        # Keep launcher alive and monitor processes
        while True:
            time.sleep(1)
            if backend_proc.poll() is not None:
                print("[-] Backend sureci beklenmedik sekilde sonlandi!")
                break
            if frontend_proc.poll() is not None:
                print("[-] Frontend sureci beklenmedik sekilde sonlandi!")
                break
    except KeyboardInterrupt:
        print("\n[*] Uygulama kapatiliyor...")
    finally:
        print("[*] Surecler temizleniyor...")
        frontend_proc.terminate()
        backend_proc.terminate()
        try:
            frontend_proc.wait(timeout=3)
            backend_proc.wait(timeout=3)
        except subprocess.TimeoutExpired:
            frontend_proc.kill()
            backend_proc.kill()
        print("[+] Tamamlandi. Iyi gunler!")

if __name__ == "__main__":
    main()
