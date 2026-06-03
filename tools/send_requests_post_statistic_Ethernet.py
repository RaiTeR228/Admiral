import psutil
import time
import requests
import os
from dotenv import load_dotenv

load_dotenv()

IP_ADDRESS = os.getenv("IP_ADDRESS")
PORT = os.getenv("PORT")
PROTOCOL = os.getenv("PROTOCOL")
API_KEY = os.getenv("API_TOKEN")
NAME_SERVER = os.getenv("NAME_SERVER")
API_URL = f"{PROTOCOL}://{IP_ADDRESS}:{PORT}/api/speed-eth/"

def get_current_network_speed(interval=1):
    """
    Вычисляет текущую скорость передачи данных для всех сетевых интерфейсов.
    Возвращает словари: скорость отправки (tx) и получения (rx) в байтах/сек.
    """
    # Получаем начальные показания
    stats_start = psutil.net_io_counters(pernic=True)
    
    # Ждем заданное время
    time.sleep(interval)
    
    # Получаем конечные показания
    stats_end = psutil.net_io_counters(pernic=True)
    
    # Словари для скоростей
    tx_speed = {}
    rx_speed = {}
    
    # Проходим по всем интерфейсам
    all_interfaces = set(stats_start.keys()) | set(stats_end.keys())
    
    for iface in all_interfaces:
        start_tx = stats_start.get(iface, psutil.net_io_counters()).bytes_sent
        start_rx = stats_start.get(iface, psutil.net_io_counters()).bytes_recv
        end_tx = stats_end.get(iface, psutil.net_io_counters()).bytes_sent
        end_rx = stats_end.get(iface, psutil.net_io_counters()).bytes_recv
        
        # Вычисляем скорость (байт в секунду)
        tx_speed[iface] = (end_tx - start_tx) / interval
        rx_speed[iface] = (end_rx - start_rx) / interval
    
    return tx_speed, rx_speed

while True:
    tx_speed, rx_speed = get_current_network_speed(interval=1)
    
    # for iface in tx_speed:
    #     print(f"{iface:35} | TX: {tx_speed[iface]/1024:8.2f} КБ/с | RX: {rx_speed[iface]/1024:8.2f} КБ/с")
    
    # print(f"{'='*80}")
    
    for iface in tx_speed:
        # Подготавливаем данные для текущего интерфейса
        data = {
            "Interface_Name": iface,
            "Eth_Sent": tx_speed[iface],      # Скорость отправки в байтах/сек
            "Eth_Recv": rx_speed[iface],      # Скорость получения в байтах/сек
            "Bytes_total_Sent": tx_speed[iface],   # Общая скорость отправки
            "Bytes_total_Recv": rx_speed[iface],   # Общая скорость получения
            "timestamp": time.time(),
            "server_name": NAME_SERVER
        }
        
        # print(f"\n📤 Отправка данных для интерфейса: {iface}")
        # print(f"   TX: {tx_speed[iface]/1024:.2f} КБ/с, RX: {rx_speed[iface]/1024:.2f} КБ/с")
        
        try:
            response = requests.post(
                API_URL,
                json=data,
                headers={"Authorization": f"Api-Key {API_KEY}"},
                timeout=5
            )
            
            if response.status_code == 200:
                print(f"Успешно (статус: {response.status_code})")
            else:
                print(f"Статус: {response.status_code}, Ответ: {response.text}")
        except Exception as e:
            print(f"Ошибка: {e}")
    
    
    time.sleep(5)