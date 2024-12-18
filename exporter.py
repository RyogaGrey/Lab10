import os
import psutil
import time
import logging
from prometheus_client import start_http_server, Gauge

# Настройка логирования
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Получаем переменные окружения для хоста, порта и интервала обновления
EXPORTER_HOST = os.getenv("EXPORTER_HOST", "0.0.0.0")
EXPORTER_PORT = int(os.getenv("EXPORTER_PORT", 8000))
UPDATE_INTERVAL = int(os.getenv("UPDATE_INTERVAL", 5))

# Метрики
cpu_usage = Gauge("cpu_usage_percent", "CPU Usage in percent")
memory_total = Gauge("memory_total_bytes", "Total Memory in bytes")
memory_used = Gauge("memory_used_bytes", "Used Memory in bytes")
disk_total = Gauge("disk_total_bytes", "Total Disk Space in bytes", ["device"])
disk_used = Gauge("disk_used_bytes", "Used Disk Space in bytes", ["device"])

def collect_metrics():
    """Сбор метрик"""
    try:
        # CPU
        cpu_percent = psutil.cpu_percent(interval=1)
        cpu_usage.set(cpu_percent)
        logger.info(f"CPU Usage: {cpu_percent}%")

        # Memory
        memory = psutil.virtual_memory()
        memory_total.set(memory.total)
        memory_used.set(memory.used)
        logger.info(f"Memory: {memory.used / 1e9:.2f} GB / {memory.total / 1e9:.2f} GB")

        # Disk
        for partition in psutil.disk_partitions():
            try:
                disk = psutil.disk_usage(partition.mountpoint)
                disk_total.labels(device=partition.device).set(disk.total)
                disk_used.labels(device=partition.device).set(disk.used)
                logger.info(
                    f"Disk ({partition.device}): {disk.used / 1e9:.2f} GB / {disk.total / 1e9:.2f} GB"
                )
            except PermissionError:
                logger.warning(f"Permission denied for partition: {partition.device}")

    except Exception as e:
        logger.error(f"Error collecting metrics: {e}")

if __name__ == "__main__":
    # Запускаем HTTP сервер
    logger.info(f"Starting exporter at http://{EXPORTER_HOST}:{EXPORTER_PORT}/")
    start_http_server(EXPORTER_PORT, addr=EXPORTER_HOST)

    # Бесконечный цикл для обновления метрик
    try:
        while True:
            collect_metrics()
            time.sleep(UPDATE_INTERVAL)
    except KeyboardInterrupt:
        logger.info("Экспортер остановлен.")
