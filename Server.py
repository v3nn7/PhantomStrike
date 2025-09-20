import socket
import threading
import logging
import configparser
import os
import signal
import sys
from datetime import datetime

# Load configuration
config = configparser.ConfigParser()
config.read('server_config.ini')

HOST = config.get('SERVER', 'HOST', fallback='0.0.0.0')
PORT = int(config.get('SERVER', 'PORT', fallback='12345'))
MAX_CONNECTIONS = int(config.get('SERVER', 'MAX_CONNECTIONS', fallback='5'))
BUFFER_SIZE = int(config.get('SERVER', 'BUFFER_SIZE', fallback='1024'))

# Set up logging
logging.basicConfig(
    filename='server.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Also log to console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

# Global variable to control server shutdown
server_running = True

def signal_handler(sig, frame):
    """
    Handle shutdown signals gracefully.
    
    Args:
        sig: Signal number
        frame: Current stack frame
    """
    global server_running
    logging.info("Shutdown signal received. Stopping server...")
    server_running = False
    sys.exit(0)

def handle_client(client_socket, client_address):
    """
    Handle individual client connections.
    
    Args:
        client_socket: Socket object for the client connection
        client_address: Tuple containing client IP and port
    """
    client_ip, client_port = client_address
    logging.info(f"New client connected: {client_ip}:{client_port}")
    
    try:
        while server_running:
            # Receive data from client
            data = client_socket.recv(BUFFER_SIZE)
            if not data:
                logging.info(f"Client {client_ip}:{client_port} disconnected")
                break
                
            # Decode and log received data
            message = data.decode('utf-8')
            logging.info(f"Received from {client_ip}:{client_port}: {message}")
            
            # Optional: Send acknowledgment back to client
            try:
                ack_message = f"Server received: {message}"
                client_socket.sendall(ack_message.encode('utf-8'))
                logging.debug(f"Sent acknowledgment to {client_ip}:{client_port}")
            except Exception as e:
                logging.error(f"Failed to send acknowledgment to {client_ip}:{client_port}: {e}")
                
    except socket.error as e:
        logging.error(f"Socket error with client {client_ip}:{client_port}: {e}")
    except Exception as e:
        logging.error(f"Unexpected error with client {client_ip}:{client_port}: {e}")
    finally:
        try:
            client_socket.close()
            logging.info(f"Closed connection to {client_ip}:{client_port}")
        except Exception as e:
            logging.error(f"Error closing connection to {client_ip}:{client_port}: {e}")

def start_server():
    """
    Start the server and listen for client connections.
    """
    global server_running
    
    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    try:
        # Set socket options for better performance
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        
        # Bind to host and port
        server.bind((HOST, PORT))
        server.listen(MAX_CONNECTIONS)
        
        logging.info(f"Server started successfully on {HOST}:{PORT}")
        logging.info(f"Maximum connections: {MAX_CONNECTIONS}")
        logging.info(f"Buffer size: {BUFFER_SIZE} bytes")
        logging.info("Waiting for client connections...")
        
        while server_running:
            try:
                # Accept client connection
                client_socket, client_address = server.accept()
                
                # Create thread for client handling
                client_handler = threading.Thread(
                    target=handle_client,
                    args=(client_socket, client_address),
                    daemon=True
                )
                client_handler.start()
                
            except socket.error as e:
                if server_running:
                    logging.error(f"Error accepting connection: {e}")
                break
                
    except Exception as e:
        logging.error(f"Server error: {e}")
    finally:
        try:
            server.close()
            logging.info("Server socket closed")
        except Exception as e:
            logging.error(f"Error closing server socket: {e}")

if __name__ == "__main__":
    # Check if config file exists
    if not os.path.exists('server_config.ini'):
        logging.warning("Configuration file 'server_config.ini' not found. Using default values.")
    
    start_server()