import os
import psutil
from prometheus_client import start_http_server, Gauge

# Получаем переменные окружения для хоста и порта
EXPORTER_HOST = os.getenv("EXPORTER_HOST", "0.0.0.0")
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", 8000))

# Метрики
cpu_usage = Gauge("cpu_usage_percent", "CPU Usage in percent")
memory_total = Gauge("memory_total_bytes", "Total Memory in bytes")
memory_used = Gauge("memory_used_bytes", "Used Memory in bytes")
disk_total = Gauge("disk_total_bytes", "Total Disk Space in bytes")
disk_used = Gauge("disk_used_bytes", "Used Disk Space in bytes")

def collect_metrics():
    """Сбор метрик"""
    # CPU
    cpu_percent = psutil.cpu_percent(interval=1)
    cpu_usage.set(cpu_percent)

    # Memory
    memory = psutil.virtual_memory()
    memory_total.set(memory.total)
    memory_used.set(memory.used)

    # Disk
    disk = psutil.disk_usage("/")
    disk_total.set(disk.total)
    disk_used.set(disk.used)

if __name__ == "__main__":
    # Запускаем HTTP сервер
    print(f"Starting exporter at http://{EXPORTER_HOST}:{EXPORTER_PORT}/")
    start_http_server(EXPORTER_PORT, addr=EXPORTER_HOST)

    # Бесконечный цикл для обновления метрик
    try:
        while True:
            collect_metrics()
    except KeyboardInterrupt:
        print("Экспортер остановлен.")
