# PhantomStrike - Client-Server Application

A robust Python client-server application with enhanced error handling, logging, and structured code organization.

## Project Structure

```
PhantomStrike/
├── Server.py                 # Enhanced server script
├── server_config.ini         # Server configuration
├── test_server.py           # Server unit tests
├── client/                  # Client package
│   ├── __init__.py
│   ├── client_config.ini    # Client configuration
│   ├── requirements.txt     # Client dependencies
│   ├── core/               # Core client functionality
│   │   ├── __init__.py
│   │   └── client_main.py  # Main client application
│   ├── functions/          # Utility functions
│   │   ├── __init__.py
│   │   └── data_sender.py  # Data transmission module
│   └── tests/             # Unit tests
│       ├── __init__.py
│       ├── test_client_main.py
│       └── test_data_sender.py
└── README.md              # This file
```

## Features

### Server Features
- **Multi-threaded**: Handles multiple client connections simultaneously
- **Robust Error Handling**: Graceful handling of connection errors and exceptions
- **Comprehensive Logging**: Detailed logging to both file and console
- **Configuration Management**: External configuration file support
- **Graceful Shutdown**: Proper cleanup on server termination
- **Client Acknowledgment**: Sends confirmation messages to clients

### Client Features
- **Modular Design**: Organized into core and utility modules
- **System Information Collection**: Gathers and sends system details
- **Interactive Mode**: Manual data entry and command interface
- **Automated Mode**: Predefined sequence of operations
- **Retry Logic**: Automatic retry on connection failures
- **Comprehensive Logging**: Detailed operation logging

## Installation

### Prerequisites
- **Python 3.7+** (tested with Python 3.9+)
- **No external dependencies required** - uses only Python standard library

### Quick Setup

1. **Download/Clone the project**
   ```bash
   git clone <repository-url>
   cd PhantomStrike
   ```

2. **Verify Python installation**
   ```bash
   python --version
   # Should show Python 3.7 or higher
   ```

3. **No additional installation required** - ready to use!

### Client Setup

1. **Navigate to client directory**
   ```bash
   cd client
   ```

2. **Configure client (optional)**
   - Edit `client_config.ini` to change server settings
   - Default settings work for local testing

3. **Run client**
   ```bash
   # Automated mode (default)
   python core/client_main.py
   
   # Interactive mode
   python core/client_main.py interactive
   ```

### Server Setup

1. **Configure server (optional)**
   - Edit `server_config.ini` to change port/host settings
   - Default settings work for local testing

2. **Run server**
   ```bash
   python Server.py
   ```

### Compilation to Executable (Optional)

#### Using PyInstaller

1. **Install PyInstaller**
   ```bash
   pip install pyinstaller
   ```

2. **Compile Server**
   ```bash
   pyinstaller --onefile --name PhantomStrike-Server Server.py
   ```

3. **Compile Client**
   ```bash
   cd client
   pyinstaller --onefile --name PhantomStrike-Client core/client_main.py
   ```

4. **Compiled executables will be in `dist/` folder**

#### Using cx_Freeze

1. **Install cx_Freeze**
   ```bash
   pip install cx_Freeze
   ```

2. **Create setup script for server**
   ```python
   # setup_server.py
   from cx_Freeze import setup, Executable
   
   setup(
       name="PhantomStrike-Server",
       version="1.0.0",
       executables=[Executable("Server.py")]
   )
   ```

3. **Create setup script for client**
   ```python
   # setup_client.py
   from cx_Freeze import setup, Executable
   
   setup(
       name="PhantomStrike-Client",
       version="1.0.0",
       executables=[Executable("client/core/client_main.py")]
   )
   ```

4. **Compile**
   ```bash
   python setup_server.py build
   python setup_client.py build
   ```

### Docker Setup (Optional)

1. **Create Dockerfile for server**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY . .
   EXPOSE 12345
   CMD ["python", "Server.py"]
   ```

2. **Create Dockerfile for client**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY client/ .
   CMD ["python", "core/client_main.py"]
   ```

3. **Build and run**
   ```bash
   docker build -t phantomstrike-server .
   docker build -t phantomstrike-client -f client/Dockerfile .
   ```

### Platform-Specific Instructions

#### Windows

1. **Download Python** from [python.org](https://python.org)
2. **Install Python** with "Add to PATH" option checked
3. **Open Command Prompt** or PowerShell
4. **Navigate to project folder**
   ```cmd
   cd C:\path\to\PhantomStrike
   ```
5. **Run applications**
   ```cmd
   # Terminal 1 - Server
   python Server.py
   
   # Terminal 2 - Client
   cd client
   python core\client_main.py
   ```

#### Linux/macOS

1. **Install Python** (if not already installed)
   ```bash
   # Ubuntu/Debian
   sudo apt update && sudo apt install python3 python3-pip
   
   # CentOS/RHEL
   sudo yum install python3 python3-pip
   
   # macOS (with Homebrew)
   brew install python3
   ```

2. **Make scripts executable** (optional)
   ```bash
   chmod +x Server.py
   chmod +x client/core/client_main.py
   ```

3. **Run applications**
   ```bash
   # Terminal 1 - Server
   python3 Server.py
   
   # Terminal 2 - Client
   cd client
   python3 core/client_main.py
   ```

### Troubleshooting Installation

#### Common Issues

1. **"python not found" error**
   - Windows: Add Python to PATH or use `py` instead of `python`
   - Linux/macOS: Use `python3` instead of `python`

2. **Permission denied errors**
   - Linux/macOS: Use `sudo` for system-wide installation
   - Or install in user directory with `--user` flag

3. **Module not found errors**
   - Ensure you're in the correct directory
   - Check Python version compatibility

4. **Port already in use**
   - Change port in configuration files
   - Kill existing process: `lsof -ti:12345 | xargs kill` (Linux/macOS)

## Configuration

### Server Configuration (`server_config.ini`)
```ini
[SERVER]
HOST = 0.0.0.0
PORT = 12345
MAX_CONNECTIONS = 5
BUFFER_SIZE = 1024

[LOGGING]
LOG_LEVEL = INFO
LOG_FILE = server.log
CONSOLE_OUTPUT = true
```

### Client Configuration (`client/client_config.ini`)
```ini
[CLIENT]
SERVER_HOST = 127.0.0.1
SERVER_PORT = 12345
CONNECTION_TIMEOUT = 10
RETRY_ATTEMPTS = 3

[LOGGING]
LOG_LEVEL = INFO
LOG_FILE = client.log
CONSOLE_OUTPUT = true
```

## Usage

### Starting the Server

```bash
python Server.py
```

The server will:
- Start listening on the configured host and port
- Log all activities to `server.log` and console
- Handle multiple client connections
- Send acknowledgment messages to clients

### Running the Client

#### Automated Mode (Default)
```bash
cd client
python core/client_main.py
```

#### Interactive Mode
```bash
cd client
python core/client_main.py interactive
```

#### Available Commands in Interactive Mode
- `info` - Send system information to server
- `quit` - Exit the client
- Any other text - Send as message to server

### Client Features

#### System Information Collection
The client automatically collects and sends:
- Operating system details
- Platform information
- Python version
- Hardware information
- Timestamp

#### Error Handling
- Connection retry with exponential backoff
- Graceful handling of network errors
- Comprehensive error logging

## Testing

### Run Server Tests
```bash
python test_server.py
```

### Run Client Tests
```bash
cd client
python -m unittest tests.test_client_main
python -m unittest tests.test_data_sender
```

### Run All Tests
```bash
python test_server.py
cd client
python -m unittest discover tests
```

## Logging

### Server Logs
- **File**: `server.log`
- **Console**: Enabled by default
- **Format**: `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`

### Client Logs
- **File**: `client/client.log`
- **Console**: Enabled by default
- **Format**: `YYYY-MM-DD HH:MM:SS - LEVEL - MESSAGE`

## Error Handling

### Server Error Handling
- Socket errors during client handling
- Connection timeout handling
- Graceful shutdown on signals (SIGINT, SIGTERM)
- Proper resource cleanup

### Client Error Handling
- Connection timeout and retry logic
- Network error recovery
- Configuration file error handling
- Graceful degradation on failures

## Development

### Adding New Features
1. **Server**: Modify `Server.py` and add tests to `test_server.py`
2. **Client Core**: Modify `client/core/client_main.py` and add tests to `client/tests/test_client_main.py`
3. **Client Functions**: Modify `client/functions/data_sender.py` and add tests to `client/tests/test_data_sender.py`

### Code Standards
- All functions and classes have docstrings
- Comprehensive error handling
- Unit tests for all public functions
- English comments and documentation
- Logging for all significant operations

## Troubleshooting

### Common Issues

1. **Port Already in Use**
   - Change the port in configuration files
   - Check if another instance is running

2. **Connection Refused**
   - Ensure server is running
   - Check host and port configuration
   - Verify firewall settings

3. **Permission Denied**
   - Run with appropriate permissions
   - Check file system permissions

### Debug Mode
Enable debug logging by changing `LOG_LEVEL = DEBUG` in configuration files.

## License

This project is provided as-is for educational and development purposes.
