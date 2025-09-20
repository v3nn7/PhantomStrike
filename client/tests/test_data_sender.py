"""
Unit tests for data_sender module.
Tests the DataSender class and related functions.
"""

import unittest
import configparser
import socket
from unittest.mock import Mock, patch, MagicMock
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.data_sender import DataSender, send_data_to_server

class TestDataSender(unittest.TestCase):
    """Test cases for DataSender class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = configparser.ConfigParser()
        self.config['CLIENT'] = {
            'SERVER_HOST': '127.0.0.1',
            'SERVER_PORT': '12345',
            'CONNECTION_TIMEOUT': '5',
            'RETRY_ATTEMPTS': '2'
        }
        self.data_sender = DataSender(self.config)
    
    def test_initialization(self):
        """Test DataSender initialization."""
        self.assertEqual(self.data_sender.server_host, '127.0.0.1')
        self.assertEqual(self.data_sender.server_port, 12345)
        self.assertEqual(self.data_sender.connection_timeout, 5)
        self.assertEqual(self.data_sender.retry_attempts, 2)
    
    def test_initialization_with_defaults(self):
        """Test DataSender initialization with default values."""
        empty_config = configparser.ConfigParser()
        sender = DataSender(empty_config)
        self.assertEqual(sender.server_host, '127.0.0.1')
        self.assertEqual(sender.server_port, 12345)
        self.assertEqual(sender.connection_timeout, 10)
        self.assertEqual(sender.retry_attempts, 3)
    
    @patch('socket.socket')
    def test_create_connection_success(self, mock_socket):
        """Test successful connection creation."""
        mock_sock = Mock()
        mock_socket.return_value = mock_sock
        
        result = self.data_sender._create_connection()
        
        self.assertIsNotNone(result)
        mock_sock.settimeout.assert_called_once_with(5)
        mock_sock.connect.assert_called_once_with(('127.0.0.1', 12345))
    
    @patch('socket.socket')
    def test_create_connection_timeout(self, mock_socket):
        """Test connection creation with timeout."""
        mock_sock = Mock()
        mock_sock.connect.side_effect = socket.timeout()
        mock_socket.return_value = mock_sock
        
        result = self.data_sender._create_connection()
        
        self.assertIsNone(result)
    
    @patch('socket.socket')
    def test_create_connection_error(self, mock_socket):
        """Test connection creation with socket error."""
        mock_sock = Mock()
        mock_sock.connect.side_effect = socket.error("Connection refused")
        mock_socket.return_value = mock_sock
        
        result = self.data_sender._create_connection()
        
        self.assertIsNone(result)
    
    @patch.object(DataSender, '_create_connection')
    def test_send_data_once_success(self, mock_create_connection):
        """Test successful data sending in single attempt."""
        mock_socket = Mock()
        mock_socket.recv.return_value = b"ACK"
        mock_create_connection.return_value = mock_socket
        
        result = self.data_sender._send_data_once("test data")
        
        self.assertTrue(result)
        mock_socket.sendall.assert_called_once_with(b"test data")
        mock_socket.close.assert_called_once()
    
    @patch.object(DataSender, '_create_connection')
    def test_send_data_once_no_connection(self, mock_create_connection):
        """Test data sending when connection fails."""
        mock_create_connection.return_value = None
        
        result = self.data_sender._send_data_once("test data")
        
        self.assertFalse(result)
    
    @patch.object(DataSender, '_create_connection')
    def test_send_data_once_socket_error(self, mock_create_connection):
        """Test data sending with socket error."""
        mock_socket = Mock()
        mock_socket.sendall.side_effect = socket.error("Send failed")
        mock_create_connection.return_value = mock_socket
        
        result = self.data_sender._send_data_once("test data")
        
        self.assertFalse(result)
        mock_socket.close.assert_called_once()
    
    @patch.object(DataSender, '_send_data_once')
    def test_send_data_success_first_attempt(self, mock_send_once):
        """Test successful data sending on first attempt."""
        mock_send_once.return_value = True
        
        result = self.data_sender.send_data("test data")
        
        self.assertTrue(result)
        mock_send_once.assert_called_once_with("test data")
    
    @patch.object(DataSender, '_send_data_once')
    @patch('time.sleep')
    def test_send_data_retry_success(self, mock_sleep, mock_send_once):
        """Test data sending with retry logic."""
        mock_send_once.side_effect = [False, True]  # First attempt fails, second succeeds
        
        result = self.data_sender.send_data("test data")
        
        self.assertTrue(result)
        self.assertEqual(mock_send_once.call_count, 2)
        mock_sleep.assert_called_once_with(2)  # First retry after 2 seconds
    
    @patch.object(DataSender, '_send_data_once')
    @patch('time.sleep')
    def test_send_data_all_attempts_fail(self, mock_sleep, mock_send_once):
        """Test data sending when all attempts fail."""
        mock_send_once.return_value = False
        
        result = self.data_sender.send_data("test data")
        
        self.assertFalse(result)
        self.assertEqual(mock_send_once.call_count, 2)  # Should retry 2 times
        mock_sleep.assert_called_once_with(2)
    
    def test_send_data_empty_string(self):
        """Test sending empty data."""
        result = self.data_sender.send_data("")
        self.assertFalse(result)
        
        result = self.data_sender.send_data("   ")
        self.assertFalse(result)
    
    @patch.object(DataSender, '_create_connection')
    def test_send_data_with_response_success(self, mock_create_connection):
        """Test sending data and receiving response."""
        mock_socket = Mock()
        mock_socket.recv.return_value = b"Server response"
        mock_create_connection.return_value = mock_socket
        
        result = self.data_sender.send_data_with_response("test data")
        
        self.assertEqual(result, "Server response")
        mock_socket.sendall.assert_called_once_with(b"test data")
        mock_socket.close.assert_called_once()
    
    @patch.object(DataSender, '_create_connection')
    def test_send_data_with_response_no_connection(self, mock_create_connection):
        """Test sending data with response when connection fails."""
        mock_create_connection.return_value = None
        
        result = self.data_sender.send_data_with_response("test data")
        
        self.assertIsNone(result)
    
    @patch.object(DataSender, 'send_data')
    def test_test_connection(self, mock_send_data):
        """Test connection testing."""
        mock_send_data.return_value = True
        
        result = self.data_sender.test_connection()
        
        self.assertTrue(result)
        mock_send_data.assert_called_once_with("CONNECTION_TEST")
    
    @patch.object(DataSender, 'send_data_with_response')
    def test_get_server_info(self, mock_send_with_response):
        """Test getting server information."""
        mock_send_with_response.return_value = "Server info"
        
        result = self.data_sender.get_server_info()
        
        self.assertEqual(result, "Server info")
        mock_send_with_response.assert_called_once_with("GET_SERVER_INFO")

class TestSendDataToServerFunction(unittest.TestCase):
    """Test cases for send_data_to_server convenience function."""
    
    @patch('functions.data_sender.DataSender')
    def test_send_data_to_server_success(self, mock_data_sender_class):
        """Test successful data sending using convenience function."""
        mock_sender = Mock()
        mock_sender.send_data.return_value = True
        mock_data_sender_class.return_value = mock_sender
        
        result = send_data_to_server("test data")
        
        self.assertTrue(result)
        mock_sender.send_data.assert_called_once_with("test data")
    
    @patch('functions.data_sender.DataSender')
    def test_send_data_to_server_failure(self, mock_data_sender_class):
        """Test failed data sending using convenience function."""
        mock_sender = Mock()
        mock_sender.send_data.return_value = False
        mock_data_sender_class.return_value = mock_sender
        
        result = send_data_to_server("test data")
        
        self.assertFalse(result)
        mock_sender.send_data.assert_called_once_with("test data")

if __name__ == '__main__':
    unittest.main()
