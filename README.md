# Damai Ticket Purchasing Automation Program

A robust and modular automation program for purchasing tickets on the Damai platform, featuring real-time monitoring, intelligent ticket selection, and anti-detection mechanisms.

## Features

### Core Functionalities
- **Automated Login**: Support for both username/password and phone number authentication methods
- **Real-time Monitoring**: Continuously check ticket availability with configurable refresh intervals
- **Intelligent Seat Selection**: Select tickets based on user-defined preferences (price range, section, row, seat type)
- **Automated Checkout**: Streamlined order submission and payment method selection

### Anti-detection Mechanisms
- Random delays between actions
- User-agent rotation
- Browser fingerprint obfuscation
- Automation feature detection prevention

### Error Handling & Reliability
- Comprehensive error handling for network failures and timeouts
- Smart retry logic with exponential backoff
- Detailed logging for troubleshooting
- Configurable session management

### Configuration Options
- YAML-based configuration for easy customization
- User-friendly parameter setup
- Modular design for easy extension

## Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup Steps

1. **Clone or download the project**
   ```bash
   cd d:\T-code
   ```

2. **Install required dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**
   ```bash
   playwright install chromium
   ```

4. **Configure the program**
   Edit the `config.yaml` file with your preferences:
   ```bash
   # Example: Edit configuration using notepad
   notepad config.yaml
   ```

## Configuration

### Authentication
```yaml
login:
  username: "your_username"      # Your Damai username (optional)
  password: "your_password"      # Your Damai password (optional)
  phone_number: "13800138000"    # Your phone number for SMS login (optional)
```

### Event Settings
```yaml
event:
  event_id: "12345678"           # Event ID from Damai URL
  ticket_quantity: 2             # Number of tickets to purchase
```

### Ticket Preferences
```yaml
ticket_preferences:
  price_ranges: ["380", "580"]  # Preferred price ranges
  sections: ["内场", "看台"]       # Preferred sections
  rows: ["1-10"]                 # Preferred rows
  seat_type: "内场"               # Preferred seat type
```

### Monitoring Settings
```yaml
monitoring:
  refresh_interval: 5            # Seconds between availability checks
  max_monitoring_time: 3600      # Maximum monitoring time in seconds
```

## Usage

### Basic Usage
```bash
python damai_ticket.py
```

### Running with Custom Configuration
```bash
python damai_ticket.py --config custom_config.yaml
```

## Workflow

1. **Initialization**: The program loads configuration and sets up logging
2. **Browser Setup**: Launches a Chrome browser with anti-detection settings
3. **Login**: Automatically logs in to Damai using configured credentials
4. **Monitoring**: Continuously checks ticket availability for the target event
5. **Ticket Selection**: Automatically selects tickets based on user preferences
6. **Checkout**: Proceeds to checkout and selects payment method
7. **Completion**: Notifies user and logs the results

## Logging

The program generates detailed logs in the specified log file (`damai_ticket.log` by default). Logs include:
- Program startup and shutdown information
- Login attempts and results
- Ticket availability checks
- Selection and checkout process
- Errors and exceptions

## Important Notes

### Legal and Ethical Considerations
- **Compliance**: This program is intended for personal use only. Ensure you comply with Damai's terms of service
- **Fair Usage**: Avoid using the program to purchase excessive tickets or engage in scalping activities
- **Responsibility**: The user is solely responsible for any consequences arising from the use of this program

### Anti-detection Best Practices
- Avoid running multiple instances simultaneously
- Use reasonable refresh intervals (minimum 5 seconds recommended)
- Consider using proxies for extended usage
- Monitor the program's behavior to avoid detection

### Troubleshooting
- **Login Issues**: If automated login fails, try manual login and then run the program
- **Detection Problems**: Reduce the refresh frequency and increase random delays
- **Network Errors**: Check your internet connection and adjust retry settings
- **Element Not Found**: The program may need updates if Damai changes its page structure

## Technical Details

### Architecture
- **Modular Design**: Separate components for configuration, logging, browser automation, and ticket purchasing
- **Playwright Integration**: Uses Playwright for robust browser automation
- **YAML Configuration**: Easy-to-edit configuration file format
- **Comprehensive Logging**: Detailed logging for debugging and monitoring

### Dependencies
- `playwright`: Browser automation framework
- `requests`: HTTP library for API requests
- `pyyaml`: YAML configuration parsing
- `loguru`: Modern logging library
- `fake-useragent`: User-agent generation for rotation
- `python-dotenv`: Environment variable loading

## Development

### Extending the Program
- Add new authentication methods in the `login` method
- Implement advanced seat selection algorithms in `_select_ticket_type`
- Add support for additional payment methods
- Enhance anti-detection mechanisms

### Testing
- Test the program with various event scenarios
- Validate anti-detection features in different environments
- Test error handling with simulated network issues
- Verify compatibility with different Damai page structures

## Disclaimer

This program is provided for educational and research purposes only. The author does not encourage or condone any illegal or unethical use of this software. Users are responsible for ensuring their use of this program complies with all applicable laws and website terms of service.

The author makes no guarantees about the program's performance, reliability, or ability to successfully purchase tickets. Use at your own risk.

## License

This project is open source and available under the MIT License.
