# monitor_serial.py
import serial
import serial.tools.list_ports
import time

def monitor_port(port, baudrate=9600):
    """Moniteur série simple"""
    
    ser = serial.Serial(port, baudrate, timeout=0.1)
    print(f"Monitoring {port} at {baudrate} bauds")
    print("Press Ctrl+C to stop")
    print("-" * 50)
    
    try:
        while True:
            # Lire les données
            if ser.in_waiting:
                data = ser.read(ser.in_waiting)
                print(f"RX ({len(data)}): {data.hex()} | {data}")
            
            # Attendre un peu
            time.sleep(0.01)
            
    except KeyboardInterrupt:
        print("\nMonitoring stopped")
    finally:
        ser.close()

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        monitor_port(sys.argv[1])
    else:
        print("Usage: python monitor_serial.py <port>")