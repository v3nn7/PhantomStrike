"""
Unit tests for client_main module.
Tests the PhantomStrikeClient class and main functionality.
"""

import unittest
import configparser
import os
import sys
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.client_main import PhantomStrikeClient

class TestPhantomStrikeClient(unittest.TestCase):
    """Test cases for PhantomStrikeClient class."""
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.config = configparser.ConfigParser()
        self.config['CLIENT'] = {
            'SERVER_HOST': '127.0.0.1',
            'SERVER_PORT': '12345',
            'CONNECTION_TIMEOUT': '10',
            'RETRY_ATTEMPTS': '3'
        }
        self.config['LOGGING'] = {
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'test_client.log',
            'CONSOLE_OUTPUT': 'false'
        }
    
    @patch('core.client_main.DataSender')
    def test_initialization_with_config(self, mock_data_sender):
        """Test client initialization with configuration."""
        mock_sender = Mock()
        mock_data_sender.return_value = mock_sender
        
        client = PhantomStrikeClient()
        
        self.assertIsNotNone(client.config)
        self.assertIsNotNone(client.data_sender)
        mock_data_sender.assert_called_once()
    
    def test_get_default_config(self):
        """Test default configuration creation."""
        client = PhantomStrikeClient()
        default_config = client._get_default_config()
        
        self.assertEqual(default_config.get('CLIENT', 'SERVER_HOST'), '127.0.0.1')
        self.assertEqual(default_config.get('CLIENT', 'SERVER_PORT'), '12345')
        self.assertEqual(default_config.get('CLIENT', 'CONNECTION_TIMEOUT'), '10')
        self.assertEqual(default_config.get('CLIENT', 'RETRY_ATTEMPTS'), '3')
    
    @patch('platform.platform')
    @patch('platform.system')
    @patch('platform.release')
    @patch('platform.version')
    @patch('platform.machine')
    @patch('platform.processor')
    @patch('platform.python_version')
    def test_collect_system_info_success(self, mock_python_version, mock_processor, 
                                       mock_machine, mock_version, mock_release, 
                                       mock_system, mock_platform):
        """Test successful system information collection."""
        # Set up mock return values
        mock_platform.return_value = "Windows-10-10.0.19041-SP0"
        mock_system.return_value = "Windows"
        mock_release.return_value = "10"
        mock_version.return_value = "10.0.19041"
        mock_machine.return_value = "AMD64"
        mock_processor.return_value = "Intel64 Family 6 Model 142 Stepping 10, GenuineIntel"
        mock_python_version.return_value = "3.9.0"
        
        client = PhantomStrikeClient()
        client.config = self.config
        
        system_info = client.collect_system_info()
        
        self.assertIn('platform', system_info)
        self.assertIn('system', system_info)
        self.assertIn('release', system_info)
        self.assertIn('version', system_info)
        self.assertIn('machine', system_info)
        self.assertIn('processor', system_info)
        self.assertIn('python_version', system_info)
        self.assertIn('timestamp', system_info)
        self.assertEqual(system_info['platform'], "Windows-10-10.0.19041-SP0")
        self.assertEqual(system_info['system'], "Windows")
    
    def test_collect_system_info_error(self):
        """Test system information collection with error."""
        with patch('platform.platform', side_effect=Exception("Platform error")):
            client = PhantomStrikeClient()
            client.config = self.config
            
            system_info = client.collect_system_info()
            
            self.assertIn('error', system_info)
            self.assertIn('timestamp', system_info)
            self.assertEqual(system_info['error'], "Platform error")
    
    @patch('core.client_main.DataSender')
    def test_send_test_message_success(self, mock_data_sender_class):
        """Test successful test message sending."""
        mock_data_sender = Mock()
        mock_data_sender.send_data.return_value = True
        mock_data_sender_class.return_value = mock_data_sender
        
        client = PhantomStrikeClient()
        client.config = self.config
        client.data_sender = mock_data_sender
        
        client.send_test_message("Test message")
        
        mock_data_sender.send_data.assert_called_once_with("Test message")
    
    @patch('core.client_main.DataSender')
    def test_send_test_message_failure(self, mock_data_sender_class):
        """Test failed test message sending."""
        mock_data_sender = Mock()
        mock_data_sender.send_data.return_value = False
        mock_data_sender_class.return_value = mock_data_sender
        
        client = PhantomStrikeClient()
        client.config = self.config
        client.data_sender = mock_data_sender
        
        # Should not raise exception, just log error
        client.send_test_message("Test message")
        
        mock_data_sender.send_data.assert_called_once_with("Test message")
    
    @patch.object(PhantomStrikeClient, 'collect_system_info')
    @patch('core.client_main.DataSender')
    def test_send_system_info_success(self, mock_data_sender_class, mock_collect_info):
        """Test successful system information sending."""
        mock_collect_info.return_value = {'platform': 'Windows', 'system': 'Windows'}
        mock_data_sender = Mock()
        mock_data_sender.send_data.return_value = True
        mock_data_sender_class.return_value = mock_data_sender
        
        client = PhantomStrikeClient()
        client.config = self.config
        client.data_sender = mock_data_sender
        
        client.send_system_info()
        
        mock_collect_info.assert_called_once()
        mock_data_sender.send_data.assert_called_once()
        # Check that the data contains system info
        call_args = mock_data_sender.send_data.call_args[0][0]
        self.assertIn("System Info:", call_args)
    
    @patch.object(PhantomStrikeClient, 'collect_system_info')
    @patch('core.client_main.DataSender')
    def test_send_system_info_failure(self, mock_data_sender_class, mock_collect_info):
        """Test failed system information sending."""
        mock_collect_info.return_value = {'platform': 'Windows', 'system': 'Windows'}
        mock_data_sender = Mock()
        mock_data_sender.send_data.return_value = False
        mock_data_sender_class.return_value = mock_data_sender
        
        client = PhantomStrikeClient()
        client.config = self.config
        client.data_sender = mock_data_sender
        
        # Should not raise exception, just log error
        client.send_system_info()
        
        mock_collect_info.assert_called_once()
        mock_data_sender.send_data.assert_called_once()
    
    @patch('builtins.input')
    @patch.object(PhantomStrikeClient, 'send_test_message')
    @patch.object(PhantomStrikeClient, 'send_system_info')
    def test_run_interactive_mode_quit(self, mock_send_system_info, mock_send_test_message, mock_input):
        """Test interactive mode with quit command."""
        mock_input.side_effect = ['quit']
        
        client = PhantomStrikeClient()
        client.config = self.config
        
        client.run_interactive_mode()
        
        mock_send_test_message.assert_not_called()
        mock_send_system_info.assert_not_called()
    
    @patch('builtins.input')
    @patch.object(PhantomStrikeClient, 'send_test_message')
    @patch.object(PhantomStrikeClient, 'send_system_info')
    def test_run_interactive_mode_info_command(self, mock_send_system_info, mock_send_test_message, mock_input):
        """Test interactive mode with info command."""
        mock_input.side_effect = ['info', 'quit']
        
        client = PhantomStrikeClient()
        client.config = self.config
        
        client.run_interactive_mode()
        
        mock_send_system_info.assert_called_once()
        mock_send_test_message.assert_not_called()
    
    @patch('builtins.input')
    @patch.object(PhantomStrikeClient, 'send_test_message')
    @patch.object(PhantomStrikeClient, 'send_system_info')
    def test_run_interactive_mode_message(self, mock_send_system_info, mock_send_test_message, mock_input):
        """Test interactive mode with message sending."""
        mock_input.side_effect = ['Hello World', 'quit']
        
        client = PhantomStrikeClient()
        client.config = self.config
        
        client.run_interactive_mode()
        
        mock_send_test_message.assert_called_once_with('Hello World')
        mock_send_system_info.assert_not_called()
    
    @patch('builtins.input')
    @patch.object(PhantomStrikeClient, 'send_test_message')
    @patch.object(PhantomStrikeClient, 'send_system_info')
    def test_run_interactive_mode_empty_input(self, mock_send_system_info, mock_send_test_message, mock_input):
        """Test interactive mode with empty input."""
        mock_input.side_effect = ['', 'quit']
        
        client = PhantomStrikeClient()
        client.config = self.config
        
        client.run_interactive_mode()
        
        mock_send_test_message.assert_not_called()
        mock_send_system_info.assert_not_called()
    
    @patch('builtins.input', side_effect=KeyboardInterrupt)
    def test_run_interactive_mode_keyboard_interrupt(self, mock_input):
        """Test interactive mode with keyboard interrupt."""
        client = PhantomStrikeClient()
        client.config = self.config
        
        # Should not raise exception
        client.run_interactive_mode()
    
    @patch('time.sleep')
    @patch.object(PhantomStrikeClient, 'send_test_message')
    @patch.object(PhantomStrikeClient, 'send_system_info')
    def test_run_automated_mode(self, mock_send_system_info, mock_send_test_message, mock_sleep):
        """Test automated mode execution."""
        client = PhantomStrikeClient()
        client.config = self.config
        
        client.run_automated_mode()
        
        # Should call send_test_message twice and send_system_info once
        self.assertEqual(mock_send_test_message.call_count, 2)
        mock_send_system_info.assert_called_once()
        # Should sleep twice
        self.assertEqual(mock_sleep.call_count, 2)

class TestMainFunction(unittest.TestCase):
    """Test cases for main function."""
    
    @patch('sys.argv', ['client_main.py', 'interactive'])
    @patch.object(PhantomStrikeClient, 'run_interactive_mode')
    def test_main_interactive_mode(self, mock_run_interactive):
        """Test main function with interactive mode."""
        from core.client_main import main
        
        main()
        
        mock_run_interactive.assert_called_once()
    
    @patch('sys.argv', ['client_main.py', 'automated'])
    @patch.object(PhantomStrikeClient, 'run_automated_mode')
    def test_main_automated_mode(self, mock_run_automated):
        """Test main function with automated mode."""
        from core.client_main import main
        
        main()
        
        mock_run_automated.assert_called_once()
    
    @patch('sys.argv', ['client_main.py'])
    @patch.object(PhantomStrikeClient, 'run_automated_mode')
    def test_main_default_mode(self, mock_run_automated):
        """Test main function with default mode."""
        from core.client_main import main
        
        main()
        
        mock_run_automated.assert_called_once()
    
    @patch('sys.argv', ['client_main.py', 'invalid'])
    @patch.object(PhantomStrikeClient, 'run_automated_mode')
    def test_main_invalid_mode(self, mock_run_automated):
        """Test main function with invalid mode."""
        from core.client_main import main
        
        main()
        
        mock_run_automated.assert_called_once()

if __name__ == '__main__':
    unittest.main()
