"""
Data transmission module for PhantomStrike client.
This module handles all communication with the server.
"""

import socket
import logging
import time
from typing import Optional

class DataSender:
    """
    Handles data transmission to the server.
    Provides methods for sending data with error handling and retry logic.
    """
    
    def __init__(self, config):
        """
        Initialize the data sender with configuration.
        
        Args:
            config: Configuration object containing server settings
        """
        self.config = config
        self.server_host = config.get('CLIENT', 'SERVER_HOST', fallback='127.0.0.1')
        self.server_port = int(config.get('CLIENT', 'SERVER_PORT', fallback='12345'))
        self.connection_timeout = int(config.get('CLIENT', 'CONNECTION_TIMEOUT', fallback='10'))
        self.retry_attempts = int(config.get('CLIENT', 'RETRY_ATTEMPTS', fallback='3'))
        
    def _create_connection(self) -> Optional[socket.socket]:
        """
        Create a connection to the server.
        
        Returns:
            socket.socket or None: Connected socket or None if failed
        """
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.settimeout(self.connection_timeout)
            client_socket.connect((self.server_host, self.server_port))
            logging.debug(f"Connected to server {self.server_host}:{self.server_port}")
            return client_socket
        except socket.timeout:
            logging.error(f"Connection timeout to {self.server_host}:{self.server_port}")
            return None
        except socket.error as e:
            logging.error(f"Socket error connecting to {self.server_host}:{self.server_port}: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error connecting to server: {e}")
            return None
    
    def _send_data_once(self, data: str) -> bool:
        """
        Send data to server in a single attempt.
        
        Args:
            data (str): Data to send
            
        Returns:
            bool: True if successful, False otherwise
        """
        client_socket = None
        try:
            # Create connection
            client_socket = self._create_connection()
            if not client_socket:
                return False
            
            # Send data
            encoded_data = data.encode('utf-8')
            client_socket.sendall(encoded_data)
            logging.debug(f"Data sent successfully: {data[:50]}...")
            
            # Try to receive acknowledgment
            try:
                response = client_socket.recv(1024)
                if response:
                    ack_message = response.decode('utf-8')
                    logging.debug(f"Received acknowledgment: {ack_message}")
            except socket.timeout:
                logging.warning("No acknowledgment received from server")
            except Exception as e:
                logging.warning(f"Error receiving acknowledgment: {e}")
            
            return True
            
        except socket.error as e:
            logging.error(f"Socket error sending data: {e}")
            return False
        except Exception as e:
            logging.error(f"Unexpected error sending data: {e}")
            return False
        finally:
            if client_socket:
                try:
                    client_socket.close()
                    logging.debug("Connection closed")
                except Exception as e:
                    logging.warning(f"Error closing connection: {e}")
    
    def send_data(self, data: str) -> bool:
        """
        Send data to server with retry logic.
        
        Args:
            data (str): Data to send to server
            
        Returns:
            bool: True if data was sent successfully, False otherwise
        """
        if not data or not data.strip():
            logging.warning("Empty data provided, nothing to send")
            return False
        
        logging.info(f"Attempting to send data to {self.server_host}:{self.server_port}")
        logging.debug(f"Data content: {data}")
        
        for attempt in range(1, self.retry_attempts + 1):
            logging.debug(f"Attempt {attempt}/{self.retry_attempts}")
            
            if self._send_data_once(data):
                logging.info(f"Data sent successfully on attempt {attempt}")
                return True
            
            if attempt < self.retry_attempts:
                wait_time = attempt * 2  # Exponential backoff
                logging.warning(f"Attempt {attempt} failed, retrying in {wait_time} seconds...")
                time.sleep(wait_time)
            else:
                logging.error(f"All {self.retry_attempts} attempts failed")
        
        return False
    
    def send_data_with_response(self, data: str) -> Optional[str]:
        """
        Send data to server and return the response.
        
        Args:
            data (str): Data to send to server
            
        Returns:
            str or None: Server response or None if failed
        """
        client_socket = None
        try:
            # Create connection
            client_socket = self._create_connection()
            if not client_socket:
                return None
            
            # Send data
            encoded_data = data.encode('utf-8')
            client_socket.sendall(encoded_data)
            logging.debug(f"Data sent: {data}")
            
            # Receive response
            response = client_socket.recv(1024)
            if response:
                response_str = response.decode('utf-8')
                logging.debug(f"Received response: {response_str}")
                return response_str
            else:
                logging.warning("No response received from server")
                return None
                
        except socket.error as e:
            logging.error(f"Socket error in send_data_with_response: {e}")
            return None
        except Exception as e:
            logging.error(f"Unexpected error in send_data_with_response: {e}")
            return None
        finally:
            if client_socket:
                try:
                    client_socket.close()
                except Exception as e:
                    logging.warning(f"Error closing connection: {e}")
    
    def test_connection(self) -> bool:
        """
        Test connection to the server.
        
        Returns:
            bool: True if connection successful, False otherwise
        """
        logging.info(f"Testing connection to {self.server_host}:{self.server_port}")
        return self.send_data("CONNECTION_TEST")
    
    def get_server_info(self) -> Optional[str]:
        """
        Get server information by sending a special request.
        
        Returns:
            str or None: Server information or None if failed
        """
        return self.send_data_with_response("GET_SERVER_INFO")

def send_data_to_server(data: str, config_file: str = 'client_config.ini') -> bool:
    """
    Convenience function to send data to server.
    
    Args:
        data (str): Data to send
        config_file (str): Configuration file path
        
    Returns:
        bool: True if successful, False otherwise
    """
    import configparser
    import os
    
    # Load configuration
    config = configparser.ConfigParser()
    config_path = os.path.join(os.path.dirname(__file__), '..', config_file)
    
    if not os.path.exists(config_path):
        logging.warning(f"Configuration file '{config_path}' not found. Using default values.")
        config['CLIENT'] = {
            'SERVER_HOST': '127.0.0.1',
            'SERVER_PORT': '12345',
            'CONNECTION_TIMEOUT': '10',
            'RETRY_ATTEMPTS': '3'
        }
    else:
        config.read(config_path)
    
    # Create sender and send data
    sender = DataSender(config)
    return sender.send_data(data)
