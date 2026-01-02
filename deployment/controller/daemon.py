import socket
import os
import psutil
import time
import threading
import logging


logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


# Configuration
DAEMON_PORT = int(os.getenv("DAEMON_PORT", "5555"))
DAEMON_HOST = os.getenv("DAEMON_HOST", "0.0.0.0")


def get_pinned_cpu_usage():
    """
    Calculates the average usage of the cores assigned to the container.
    """
    try:
        pinned_cpus = os.sched_getaffinity(0)

        # All CPUs usage
        all_cpus_usage = psutil.cpu_percent(interval=0.5, percpu=True)

        # Filter usage for pinned CPUs
        pinned_cpus_avg_usage = [all_cpus_usage[cpu_id] for cpu_id in pinned_cpus]

        if not pinned_cpus_avg_usage:
            return 0.0
        return sum(pinned_cpus_avg_usage) / len(pinned_cpus_avg_usage)
    
    except Exception as e:
        print(f"Error getting pinned CPU usage: {e}")
        return 100.0  # Assume full usage on error. Fail-safe: Assume busy if can't read
    

def handle_client(conn):
    try:
        # Get the real load of pinned cpus
        load = get_pinned_cpu_usage()

        # LOGIC:
        # Logd > 90% -> BUSY
        # Loadd < 70% -> IDLE
        if load > 85.0:
            resp = b"drain\n"
            logger.info(f"⚠️  Reporting DRAIN (high load): {load:.1f}%")
        else:
            weight = max(1, int(100 - load))
            resp = f"ready {weight}%\n".encode('ascii')
            logger.info(f"✅ Reporting UP (load): {load:.1f}%, weight: {weight}%")
        
        conn.sendall(resp)

    except Exception as e:
        logger.error(f"Error handling client: {e}")
    finally:
        conn.close()


def start_daemon():
    # Prime psutil (first call is always 0)
    psutil.cpu_percent(interval=None, percpu=True)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((DAEMON_HOST, DAEMON_PORT))
    s.listen(5)
    logger.info(f"⚡ Daemon listening on {DAEMON_PORT}")

    while True:
        conn, addr = s.accept()
        t = threading.Thread(target=handle_client, args=(conn,))
        t.start()


if __name__ == "__main__":
    start_daemon()



# Instead of waiting for 0.5 seconds everytime. Calculate the value continuously
# import socket
# import os
# import psutil
# import time
# import threading

# AGENT_PORT = 5555
# AGENT_HOST = '0.0.0.0'

# # Global State
# _last_check_time = 0
# _last_cpu_times = {}

# def get_instant_pinned_cpu():
#     """
#     Calculates CPU usage instantly by comparing 
#     current counters vs the last time we checked.
#     """
#     global _last_check_time, _last_cpu_times
    
#     try:
#         # 1. Get Allowed Cores
#         allowed_cpus = os.sched_getaffinity(0)
        
#         # 2. Get Current Counters (Non-blocking!)
#         # This returns the raw "ticks" the CPU has executed since boot
#         current_cpu_times = psutil.cpu_times(percpu=True)
#         current_time = time.time()
        
#         # 3. Handle First Run (No history)
#         if _last_check_time == 0:
#             _last_check_time = current_time
#             _last_cpu_times = current_cpu_times
#             return 0.0 # Assume 0% on startup

#         # 4. Calculate Deltas
#         # We sum up the time spent "busy" (user + system) for our pinned cores
#         total_busy_delta = 0
#         total_time_delta = 0
        
#         time_diff = current_time - _last_check_time
#         # Avoid division by zero if called too fast
#         if time_diff < 0.1: 
#             return 0.0 

#         count = 0
#         for core_id in allowed_cpus:
#             # Get counters for this specific core
#             now = current_cpu_times[core_id]
#             prev = _last_cpu_times[core_id]
            
#             # Busy = User + System + Nice ...
#             # Idle = Idle + Iowait
#             # Psutil simplifies this: (busy_now - busy_prev)
            
#             # Simple Hack: Use psutil's internal math per core if possible, 
#             # but manually simpler: just rely on global average logic or use psutil.cpu_percent(interval=None)
#             pass

#         # RE-SIMPLIFIED LOGIC: 
#         # psutil.cpu_percent(interval=None, percpu=True) maintains its OWN internal state!
#         # We don't need to do the math manually. Psutil does it for us.
        
#         all_cpus_usage = psutil.cpu_percent(interval=None, percpu=True)
#         my_cores_usage = [all_cpus_usage[i] for i in allowed_cpus]
        
#         avg_load = sum(my_cores_usage) / len(my_cores_usage)
#         return avg_load

#     except Exception as e:
#         print(f"Error: {e}")
#         return 0.0

# def handle_client(conn):
#     try:
#         # This is now INSTANT (Microseconds)
#         load = get_instant_pinned_cpu()
        
#         if load > 95.0:
#             resp = b"drain\n"
#         else:
#             weight = max(1, int(100 - load))
#             resp = f"up {weight}%\n".encode('ascii')
            
#         conn.sendall(resp)
#     except Exception:
#         pass
#     finally:
#         conn.close()

# def start_server():
#     # Prime the psutil state
#     psutil.cpu_percent(interval=None, percpu=True)
    
#     s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#     s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     s.bind((AGENT_HOST, AGENT_PORT))
#     s.listen(5)
#     print(f"⚡ Instant Agent listening on {AGENT_PORT}")
    
#     while True:
#         conn, addr = s.accept()
#         # Threading is less critical now (since logic is fast), 
#         # but still good for safety.
#         t = threading.Thread(target=handle_client, args=(conn,))
#         t.start()

# if __name__ == "__main__":
#     start_server()