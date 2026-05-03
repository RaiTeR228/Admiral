import psutil
import platform
from datetime import datetime
import socket
# import GPUtil
# from tabulate import tabulate
import cpuinfo





def get_size(bytes, suffix="B"):
    """
    Scale bytes to its proper format
    e.g:
        1253656 => '1.20MB'
        1253656678 => '1.17GB'
    """
    factor = 1024
    for unit in ["", "K", "M", "G", "T", "P"]:
        if bytes < factor:
            return f"{bytes:.2f}{unit}{suffix}"
        bytes /= factor
def get_size_to_mb(bytes):
    return{bytes * 1024*1024}

def Status_Server():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "ram": psutil.virtual_memory().percent,
        #  "IO": {
            # "disk_read": get_size(psutil.disk_io_counters().read_bytes),
            # "disk_write": get_size(psutil.disk_io_counters().write_bytes),
            # "net_sent": get_size(psutil.net_io_counters().bytes_sent),
            # "net_recv": get_size(psutil.net_io_counters().bytes_recv),
        # }
    }

def System_Info():
    uname = platform.uname()
    return {
        "system": uname.system,
        "node_name": uname.node,
        "release": uname.release,
        "version": uname.version,
        "machine": uname.machine,
        # "processor": uname.processor,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        "processor_name": cpuinfo.get_cpu_info()
        # print(cpu_info['brand_raw'])
    }

def Cpu_Info():
    cpufreq = psutil.cpu_freq()
    return {
        "physical_cores": psutil.cpu_count(logical=False), 
        "total_cores": psutil.cpu_count(logical=True),
        "max_frequency": f"{cpufreq.max:.2f}Mhz",
        "min_frequency": f"{cpufreq.min:.2f}Mhz",
        "current_frequency": f"{cpufreq.current:.2f}Mhz",
        "cpu_usage_per_core": [f"Core {i}: {percentage}%" for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1))],
        "total_cpu_usage": f"{psutil.cpu_percent()}%",
    }
# print(Cpu_Info())

def Ram_Info():
    ram = psutil.virtual_memory()
    return {
        "total": get_size(ram.total),
        "available": get_size(ram.available),
        # "used": get_size(ram.used),
        "used": str(ram.used),
        "percentage": ram.percent,

# total — общий объём физической памяти в байтах;
# available — доступный объём памяти;
# used — объём используемой памяти;
# percent — процент использования памяти.
    }

def Swap_Info():
    swap = psutil.swap_memory()
    return {
        "total": get_size(swap.total),
        "free": get_size(swap.free),
        "used": (swap.used),
        "percentage": swap.percent
    }

# # Disk Information

# print("Partitions and Usage:")
def Disk_Info():
    partitions = psutil.disk_partitions()
    
    for partition in partitions:
        print(f"=== Device: {partition.device} ===")
        print(f"  Mountpoint: {partition.mountpoint}")
        print(f"  File system type: {partition.fstype}")
        try:
            partition_usage = psutil.disk_usage(partition.mountpoint)
        except PermissionError:
            print("нету прав доступа, запустите от имени администратора")
            # this can be catched due to the disk that
            # isn't ready
            continue
        print(f"  Total Size: {get_size(partition_usage.total)}")
        print(f"  Used: {get_size(partition_usage.used)}")
        print(f"  Free: {get_size(partition_usage.free)}")
        print(f"  Percentage: {partition_usage.percent}%")
    # get IO statistics since boot
    disk_io = psutil.disk_io_counters()
    print(f"Total read: {get_size(disk_io.read_bytes)}")
    print(f"Total write: {get_size(disk_io.write_bytes)}")
    
    return {"Device": partitions.device, "Mountpoint": partitions.mountpoint, "File system type": partitions.fstype, "Total Size": get_size(partition_usage.total), "Used": get_size(partition_usage.used), "Free": get_size(partition_usage.free), "Percentage": partition_usage.percent}

# # Network information

# get all network interfaces (virtual and physical)
def Network_Info():
    if_addrs = psutil.net_if_addrs()
    for interface_name, interface_addresses in if_addrs.items():
        for address in interface_addresses:
            print(f"=== Interface: {interface_name} ===")
            if str(address.family) == 'AddressFamily.AF_INET':
                print(f"  IP Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast IP: {address.broadcast}")
            elif str(address.family) == 'AddressFamily.AF_PACKET':
                print(f"  MAC Address: {address.address}")
                print(f"  Netmask: {address.netmask}")
                print(f"  Broadcast MAC: {address.broadcast}")
    # get IO statistics since boot
    net_io = psutil.net_io_counters()
    print(f"Total Bytes Sent: {get_size(net_io.bytes_sent)}")
    print(f"Total Bytes Received: {get_size(net_io.bytes_recv)}")

    return {"Interface": interface_name, "IP Address": address.address, "Netmask": address.netmask, "Broadcast IP": address.broadcast, "MAC Address": address.address, "Broadcast MAC": address.broadcast, "Total Bytes Sent": get_size(net_io.bytes_sent), "Total Bytes Received": get_size(net_io.bytes_recv)}

def get_local_ip():
    hostname = socket.gethostname()
    _, _, ip_addresses = socket.gethostbyname_ex(hostname)
    # Фильтруем loopback-адреса (начинающиеся с 127.)
    filtered_ips = [ip for ip in ip_addresses if not ip.startswith("127.")]
    return filtered_ips if filtered_ips else None 

# # GPU information
def Gpu_Info():
    # print("="*40, "GPU Details", "="*40)
    gpus = 1#GPUtil.getGPUs()
    list_gpus = []
    for gpu in gpus:
        # get the GPU id
        gpu_id = gpu.id
        # name of GPU
        gpu_name = gpu.name
        # get % percentage of GPU usage of that GPU
        gpu_load = f"{gpu.load*100}%"
        # get free memory in MB format
        gpu_free_memory = f"{gpu.memoryFree}MB"
        # get used memory
        gpu_used_memory = f"{gpu.memoryUsed}MB"
        # get total memory
        gpu_total_memory = f"{gpu.memoryTotal}MB"
        # get GPU temperature in Celsius
        gpu_temperature = f"{gpu.temperature} °C"
        gpu_uuid = gpu.uuid
        list_gpus.append((
            gpu_id, gpu_name, gpu_load, gpu_free_memory, gpu_used_memory,
            gpu_total_memory, gpu_temperature, gpu_uuid
        ))
        return {"id": gpu_id, "name": gpu_name, "load": gpu_load, "free memory": gpu_free_memory, "used memory": gpu_used_memory, "total memory": gpu_total_memory, "temperature": gpu_temperature, "uuid": gpu_uuid}

# print(tabulate(list_gpus, headers=("id", "name", "load", "free memory", "used memory", "total memory",
#                                    "temperature", "uuid")))