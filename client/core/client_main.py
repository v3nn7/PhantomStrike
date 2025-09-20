"""
Main client application for PhantomStrike.
This module serves as the entry point for the client application.
"""

import os
import sys
import logging
import configparser
import platform
import time
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from functions.data_sender import DataSender

class PhantomStrikeClient:
    """
    Main client class for PhantomStrike application.
    Handles client initialization, data collection, and communication with server.
    """
    
    def __init__(self, config_file='client_config.ini'):
        """
        Initialize the client with configuration.
        
        Args:
            config_file (str): Path to configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()
        self.data_sender = DataSender(self.config)
        self._setup_logging()
        
    def _load_config(self):
        """
        Load configuration from file.
        
        Returns:
            configparser.ConfigParser: Configuration object
        """
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', self.config_file)
        
        if not os.path.exists(config_path):
            logging.warning(f"Configuration file '{config_path}' not found. Using default values.")
            return self._get_default_config()
            
        try:
            config.read(config_path)
            logging.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logging.error(f"Error loading configuration: {e}")
            return self._get_default_config()
    
    def _get_default_config(self):
        """
        Get default configuration values.
        
        Returns:
            configparser.ConfigParser: Default configuration
        """
        config = configparser.ConfigParser()
        config['CLIENT'] = {
            'SERVER_HOST': '127.0.0.1',
            'SERVER_PORT': '12345',
            'CONNECTION_TIMEOUT': '10',
            'RETRY_ATTEMPTS': '3'
        }
        config['LOGGING'] = {
            'LOG_LEVEL': 'INFO',
            'LOG_FILE': 'client.log',
            'CONSOLE_OUTPUT': 'true'
        }
        return config
    
    def _setup_logging(self):
        """
        Set up logging configuration.
        """
        log_level = self.config.get('LOGGING', 'LOG_LEVEL', fallback='INFO')
        log_file = self.config.get('LOGGING', 'LOG_FILE', fallback='client.log')
        console_output = self.config.getboolean('LOGGING', 'CONSOLE_OUTPUT', fallback=True)
        
        # Set up logging
        logging.basicConfig(
            filename=log_file,
            level=getattr(logging, log_level.upper()),
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler if enabled
        if console_output:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(getattr(logging, log_level.upper()))
            formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            logging.getLogger().addHandler(console_handler)
    
    def collect_system_info(self):
        """
        Collect system information.
        
        Returns:
            dict: System information dictionary
        """
        try:
            system_info = {
                'platform': platform.platform(),
                'system': platform.system(),
                'release': platform.release(),
                'version': platform.version(),
                'machine': platform.machine(),
                'processor': platform.processor(),
                'python_version': platform.python_version(),
                'timestamp': datetime.now().isoformat()
            }
            logging.info("System information collected successfully")
            return system_info
        except Exception as e:
            logging.error(f"Error collecting system information: {e}")
            return {'error': str(e), 'timestamp': datetime.now().isoformat()}
    
    def send_test_message(self, message="Hello from PhantomStrike Client"):
        """
        Send a test message to the server.
        
        Args:
            message (str): Message to send
        """
        try:
            logging.info(f"Sending test message: {message}")
            success = self.data_sender.send_data(message)
            if success:
                logging.info("Test message sent successfully")
            else:
                logging.error("Failed to send test message")
        except Exception as e:
            logging.error(f"Error sending test message: {e}")
    
    def send_system_info(self):
        """
        Collect and send system information to the server.
        """
        try:
            system_info = self.collect_system_info()
            info_string = f"System Info: {system_info}"
            logging.info("Sending system information to server")
            success = self.data_sender.send_data(info_string)
            if success:
                logging.info("System information sent successfully")
            else:
                logging.error("Failed to send system information")
        except Exception as e:
            logging.error(f"Error sending system information: {e}")
    
    def run_interactive_mode(self):
        """
        Run client in interactive mode for manual data entry.
        """
        logging.info("Starting interactive mode")
        print("PhantomStrike Client - Interactive Mode")
        print("Type 'quit' to exit, 'info' to send system info, or any message to send")
        
        while True:
            try:
                user_input = input("\nEnter message (or command): ").strip()
                
                if user_input.lower() == 'quit':
                    logging.info("Exiting interactive mode")
                    break
                elif user_input.lower() == 'info':
                    self.send_system_info()
                elif user_input:
                    self.send_test_message(user_input)
                else:
                    print("Please enter a message or command")
                    
            except KeyboardInterrupt:
                logging.info("Interrupted by user")
                break
            except Exception as e:
                logging.error(f"Error in interactive mode: {e}")
                print(f"Error: {e}")
    
    def run_automated_mode(self):
        """
        Run client in automated mode with predefined actions.
        """
        logging.info("Starting automated mode")
        
        # Send initial greeting
        self.send_test_message("PhantomStrike Client started")
        
        # Wait a moment
        time.sleep(1)
        
        # Send system information
        self.send_system_info()
        
        # Wait a moment
        time.sleep(1)
        
        # Send completion message
        self.send_test_message("PhantomStrike Client automated sequence completed")
        
        logging.info("Automated mode completed")

def main():
    """
    Main entry point for the client application.
    """
    try:
        # Initialize client
        client = PhantomStrikeClient()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            mode = sys.argv[1].lower()
            if mode == 'interactive':
                client.run_interactive_mode()
            elif mode == 'automated':
                client.run_automated_mode()
            else:
                print("Usage: python client_main.py [interactive|automated]")
                print("Default: automated mode")
                client.run_automated_mode()
        else:
            # Default to automated mode
            client.run_automated_mode()
            
    except Exception as e:
        logging.error(f"Fatal error in main: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
