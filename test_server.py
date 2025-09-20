"""
Unit tests for server functionality.
Tests the server script and related functions.
"""

import unittest
import socket
import threading
import time
import configparser
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import server functions
import Server

class TestServerFunctions(unittest.TestCase):
    """Test cases for server functions."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = configparser.ConfigParser()
        self.test_config['SERVER'] = {
            'HOST': '127.0.0.1',
            'PORT': '12346',  # Use different port for testing
            'MAX_CONNECTIONS': '5',
            'BUFFER_SIZE': '1024'
        }
    
    def test_signal_handler(self):
        """Test signal handler function."""
        # Test that signal handler sets server_running to False
        Server.server_running = True
        Server.signal_handler(signal.SIGINT, None)
        self.assertFalse(Server.server_running)
    
    @patch('socket.socket')
    def test_handle_client_success(self, mock_socket_class):
        """Test successful client handling."""
        # Create mock client socket
        mock_client_socket = Mock()
        mock_client_socket.getpeername.return_value = ('127.0.0.1', 12345)
        mock_client_socket.recv.side_effect = [b"test message", b""]  # Second call returns empty (disconnect)
        
        # Test the function
        Server.handle_client(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify socket operations
        self.assertEqual(mock_client_socket.recv.call_count, 2)
        mock_client_socket.sendall.assert_called_once()
        mock_client_socket.close.assert_called_once()
    
    @patch('socket.socket')
    def test_handle_client_socket_error(self, mock_socket_class):
        """Test client handling with socket error."""
        mock_client_socket = Mock()
        mock_client_socket.getpeername.return_value = ('127.0.0.1', 12345)
        mock_client_socket.recv.side_effect = socket.error("Connection lost")
        
        # Test the function
        Server.handle_client(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify socket was closed
        mock_client_socket.close.assert_called_once()
    
    @patch('socket.socket')
    def test_handle_client_general_error(self, mock_socket_class):
        """Test client handling with general error."""
        mock_client_socket = Mock()
        mock_client_socket.getpeername.return_value = ('127.0.0.1', 12345)
        mock_client_socket.recv.side_effect = Exception("Unexpected error")
        
        # Test the function
        Server.handle_client(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify socket was closed
        mock_client_socket.close.assert_called_once()
    
    @patch('socket.socket')
    def test_handle_client_send_error(self, mock_socket_class):
        """Test client handling with send error."""
        mock_client_socket = Mock()
        mock_client_socket.getpeername.return_value = ('127.0.0.1', 12345)
        mock_client_socket.recv.return_value = b"test message"
        mock_client_socket.sendall.side_effect = Exception("Send failed")
        
        # Test the function
        Server.handle_client(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify socket was closed despite send error
        mock_client_socket.close.assert_called_once()
    
    @patch('socket.socket')
    def test_handle_client_close_error(self, mock_socket_class):
        """Test client handling with close error."""
        mock_client_socket = Mock()
        mock_client_socket.getpeername.return_value = ('127.0.0.1', 12345)
        mock_client_socket.recv.side_effect = [b"test message", b""]
        mock_client_socket.close.side_effect = Exception("Close failed")
        
        # Test the function - should not raise exception
        Server.handle_client(mock_client_socket, ('127.0.0.1', 12345))
        
        # Verify close was attempted
        mock_client_socket.close.assert_called_once()

class TestServerIntegration(unittest.TestCase):
    """Integration tests for server functionality."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_port = 12347  # Use different port for testing
        self.server_thread = None
        self.server_socket = None
    
    def tearDown(self):
        """Clean up after each test."""
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if self.server_thread and self.server_thread.is_alive():
            Server.server_running = False
            self.server_thread.join(timeout=1)
    
    def start_test_server(self):
        """Start a test server in a separate thread."""
        def run_server():
            try:
                self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind(('127.0.0.1', self.test_port))
                self.server_socket.listen(1)
                Server.server_running = True
                
                while Server.server_running:
                    try:
                        client_socket, addr = self.server_socket.accept()
                        Server.handle_client(client_socket, addr)
                    except socket.error:
                        break
            except Exception as e:
                print(f"Server error: {e}")
            finally:
                if self.server_socket:
                    self.server_socket.close()
        
        self.server_thread = threading.Thread(target=run_server, daemon=True)
        self.server_thread.start()
        time.sleep(0.1)  # Give server time to start
    
    def test_client_server_communication(self):
        """Test basic client-server communication."""
        # Start test server
        self.start_test_server()
        
        # Create client and connect
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.settimeout(5)
        
        try:
            client_socket.connect(('127.0.0.1', self.test_port))
            
            # Send test message
            test_message = "Hello from test client"
            client_socket.sendall(test_message.encode('utf-8'))
            
            # Receive acknowledgment
            response = client_socket.recv(1024)
            self.assertIsNotNone(response)
            self.assertIn(b"Server received", response)
            
        finally:
            client_socket.close()
            Server.server_running = False
    
    def test_multiple_clients(self):
        """Test server handling multiple clients."""
        # Start test server
        self.start_test_server()
        
        clients = []
        try:
            # Create multiple clients
            for i in range(3):
                client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                client_socket.settimeout(5)
                client_socket.connect(('127.0.0.1', self.test_port))
                clients.append(client_socket)
            
            # Send messages from all clients
            for i, client in enumerate(clients):
                message = f"Message from client {i}"
                client.sendall(message.encode('utf-8'))
                
                # Receive acknowledgment
                response = client.recv(1024)
                self.assertIsNotNone(response)
                self.assertIn(b"Server received", response)
            
        finally:
            for client in clients:
                client.close()
            Server.server_running = False

class TestServerConfiguration(unittest.TestCase):
    """Test cases for server configuration handling."""
    
    def test_config_loading(self):
        """Test configuration loading from file."""
        # Create temporary config file
        config_content = """
[SERVER]
HOST = 127.0.0.1
PORT = 12348
MAX_CONNECTIONS = 10
BUFFER_SIZE = 2048
"""
        with open('test_server_config.ini', 'w') as f:
            f.write(config_content)
        
        try:
            # Test config loading
            config = configparser.ConfigParser()
            config.read('test_server_config.ini')
            
            self.assertEqual(config.get('SERVER', 'HOST'), '127.0.0.1')
            self.assertEqual(config.get('SERVER', 'PORT'), '12348')
            self.assertEqual(config.get('SERVER', 'MAX_CONNECTIONS'), '10')
            self.assertEqual(config.get('SERVER', 'BUFFER_SIZE'), '2048')
            
        finally:
            # Clean up
            if os.path.exists('test_server_config.ini'):
                os.remove('test_server_config.ini')
    
    def test_config_defaults(self):
        """Test configuration with default values."""
        config = configparser.ConfigParser()
        
        # Test fallback values
        host = config.get('SERVER', 'HOST', fallback='0.0.0.0')
        port = int(config.get('SERVER', 'PORT', fallback='12345'))
        max_conn = int(config.get('SERVER', 'MAX_CONNECTIONS', fallback='5'))
        buffer_size = int(config.get('SERVER', 'BUFFER_SIZE', fallback='1024'))
        
        self.assertEqual(host, '0.0.0.0')
        self.assertEqual(port, 12345)
        self.assertEqual(max_conn, 5)
        self.assertEqual(buffer_size, 1024)

if __name__ == '__main__':
    unittest.main()
