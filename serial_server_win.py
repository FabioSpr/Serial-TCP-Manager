import socket
import serial
import threading
import signal
import queue
import logging

# ===================== CONFIG ======================= #

TCP_IP = "0.0.0.0"
TCP_PORT = 5000

BAUDRATE = 115200
LOGFILE = "serial_to_tcp.log"
WRITE_TIMEOUT = 200  # secondi

DISCOVERY_PORT = 5001
DISCOVERY_MAGIC = b"DISCOVER_TCP_BRIDGE"
DISCOVERY_REPLY = b"TCP_BRIDGE"

# ==================================================== #

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", handlers=[logging.FileHandler(LOGFILE), logging.StreamHandler()])

stop_event = threading.Event()
write_queue = queue.Queue(maxsize=100)
error_flag = False


# --------- Interrupt Handler ---------
def handle_exit(signum, frame):
    logging.info(f"[SERVER] Signal {signum} received, closing execution...")
    stop_event.set()
    # print("Stop Event: ", stop_event.is_set())


signal.signal(signal.SIGINT, handle_exit)  # Ctrl+C
signal.signal(signal.SIGTERM, handle_exit)  # chiusura processo


# ---------- Discovery Thread ----------
def discovery_server():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("", DISCOVERY_PORT))

    logging.info("[TCP] Discovery UDP active")

    while not stop_event.is_set():
        try:
            data, addr = sock.recvfrom(1024)
            if data == DISCOVERY_MAGIC:
                reply = f"{DISCOVERY_REPLY.decode()} {TCP_PORT}".encode()
                sock.sendto(reply, addr)
                logging.info("[TCP] Client connected")
        except Exception:
            continue

    sock.close()



# --------- Serial Read Thread ---------
def serial_to_tcp(ser, conn):
    global error_flag
    try:
        while not stop_event.is_set():
            data = ser.readline()
            if data:
                try:
                    conn.sendall(data)
                except (BrokenPipeError, ConnectionResetError, OSError) as e:
                    logging.warning(f"[TCP] TCP send failed: {e}")
                    logging.warning("[TCP] Client TCP disconnected (reader)")
                    stop_event.set()
                    error_flag = True
                    break
    except serial.SerialException as e:
        logging.error(f"[SERIAL] Serial reading error: {e}")
        error_flag = True
        stop_event.set()


# --------- Serial Write Thread ---------
def serial_writer(ser):
    global error_flag
    while not stop_event.is_set():
        try:
            data = write_queue.get(timeout=0.5)
        except queue.Empty:
            continue

        try:
            ser.write(data)
        except serial.SerialTimeoutException:
            logging.error("[SERIAL] Serial write Timeout")
            stop_event.set()
            error_flag = True
            break
        except serial.SerialException as e:
            logging.error(f"[SERIAL] Serial write Error: {e}")
            stop_event.set()
            error_flag = True
            break
        except Exception as e:
            logging.critical(f"[SERIAL] Generic error: {e}")
            stop_event.set()
            error_flag = True
            break


def main():
    global error_flag

    SERIAL_PORT = "COM" + input("Enter COM serial port number: ")

    # Thread per Discovery
    discovery_thread = threading.Thread(target=discovery_server, name="DiscoveryServer", daemon=True)
    discovery_thread.start()

    while True:
        stop_event.clear()
        error_flag = False

        reader = None
        writer = None
        conn = None
        
        logging.info("\n=== Waiting for new TCP session ===")

        try:
            # Apri seriale
            ser = serial.Serial(
                port=SERIAL_PORT,
                baudrate=BAUDRATE,
                bytesize=serial.EIGHTBITS,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                timeout=0.5,
                write_timeout=WRITE_TIMEOUT
            )

            logging.info(f"[TCP] Serial open on {SERIAL_PORT}")

            # Socket TCP
            server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            server.bind((TCP_IP, TCP_PORT))
            server.listen(1)
            server.settimeout(0.5)

            logging.info(f"[TCP] Server listening on port {TCP_PORT} ...")

            while not stop_event.is_set():
                try:
                    conn, addr = server.accept()
                    conn.settimeout(0.5)
                    logging.info(f"[TCP] Client connected: {addr}")
                    break
                except socket.timeout:
                    continue

            if conn is None:
                return

            # Thread per seriale → TCP
            reader = threading.Thread(target=serial_to_tcp, args=(ser, conn), name="SerialReader")

            # Thread per TCP → Seriale
            writer = threading.Thread(target=serial_writer, args=(ser,), name="SerialWriter")

            reader.start()
            writer.start()

            # TCP → Queue Loop
            while not stop_event.is_set():
                try:
                    data = conn.recv(1024)
                    if not data:
                        logging.info("[TCP] Client disconnected.")
                        break
                    write_queue.put(data, timeout=1)

                except queue.Full:
                    logging.warning("[SERIAL] Serial queue full, discarded package")
                    continue
                except socket.timeout:
                    continue
                except serial.SerialException as e:
                    logging.warning(f"[SERIAL] Serial write Error: {e}")
                    continue
                except (ConnectionResetError, BrokenPipeError, OSError) as e:
                    logging.warning(f"[SERIAL] TCP Error: {e}")
                    break

        except KeyboardInterrupt:
            logging.warning("[SERVER] Ctrl+C received, server is closing...")

        except serial.SerialException as e:
            logging.warning(f"[SERIAL] Impossible to open serial on {SERIAL_PORT}: {e}")
            error_flag = True

        finally:
            stop_event.set()

            if conn:
                try: conn.shutdown(socket.SHUT_RDWR)
                except: pass
                conn.close()

            if reader: reader.join(timeout=2)

            if writer: writer.join(timeout=2)

            try: ser.close()
            except: pass

            try: server.close()
            except: pass

            if error_flag:
                logging.warning("\n!!! Error received during execution !!! See log for details")

            logging.info("\n=== Session closed. Ready for next client. ===\n")


if __name__ == "__main__":
    main()
    input("\n\nPress ENTER to continue...")