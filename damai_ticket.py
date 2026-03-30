#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Damai Ticket Purchasing Automation Program
"""

import time
import random
import yaml
import os
import threading
import queue
from loguru import logger
from fake_useragent import UserAgent
from playwright.sync_api import sync_playwright
from dotenv import load_dotenv
from urllib.error import URLError, HTTPError
from http.client import HTTPException
from requests.exceptions import ConnectionError, Timeout, HTTPError as RequestsHTTPError

# Load environment variables
load_dotenv()

class DamaiTicketSystem:
    """Main Damai Ticket Purchasing System"""
    
    def __init__(self, config_path="config.yaml"):
        """Initialize the ticket system"""
        self.config = self._load_config(config_path)
        self._setup_logging()
        self._setup_anti_detect()
        self.retry_manager = self.RetryManager(self)  # Initialize retry manager
        self.browser = None
        self.page = None
        self.session = None
        
    def _load_config(self, config_path):
        """Load configuration from YAML file"""
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            # Load default configuration as fallback
            with open("config.yaml", 'r', encoding='utf-8') as f:
                default_config = yaml.safe_load(f)
            
            # Merge config with defaults, preserving user values
            def merge_dicts(default, custom):
                """Recursively merge custom dict into default dict"""
                for key, value in default.items():
                    if key not in custom:
                        custom[key] = value
                    elif isinstance(value, dict) and isinstance(custom[key], dict):
                        merge_dicts(value, custom[key])
                return custom
            
            merged_config = merge_dicts(default_config, config)
            logger.info("Configuration loaded and merged with defaults successfully")
            return merged_config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            raise
    
    def _setup_logging(self):
        """Setup logging configuration"""
        log_config = self.config['logging']
        logger.remove()  # Remove default logger
        
        # Add file logger
        logger.add(
            log_config['log_file'],
            level=log_config['level'],
            rotation=f"{log_config['max_log_size']} MB",
            retention=log_config['backup_count']
        )
        
        # Add console logger
        logger.add(
            sink=lambda msg: print(msg, end=""),
            level=log_config['level']
        )
        
        logger.info("Logging setup completed")
    
    def _setup_anti_detect(self):
        """Setup anti-detection mechanisms"""
        self._rotate_user_agent = self.config['anti_detect']['rotate_user_agent']
        self.ua = UserAgent() if self._rotate_user_agent else None
        self._fixed_user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36"
        logger.info("Anti-detection setup completed")
    
    def _random_delay(self):
        """Generate a random delay to avoid detection"""
        delay_min = self.config['anti_detect']['random_delay_min']
        delay_max = self.config['anti_detect']['random_delay_max']
        delay = random.uniform(delay_min, delay_max)
        time.sleep(delay)
    
    def _get_user_agent(self):
        """Get a random user agent if rotation is enabled"""
        # Check current rotation setting in config (not cached value)
        if self.config['anti_detect']['rotate_user_agent'] and self.ua:
            return self.ua.random
        return self._fixed_user_agent
    
    class RetryManager:
        """Robust network connection retry manager with thread safety and non-blocking support"""
        
        def __init__(self, parent):
            """Initialize retry manager"""
            self.parent = parent
            self.config = parent.config['advanced']
            self._lock = threading.RLock()  # Reentrant lock for thread safety
            self._retry_queues = {}  # Queue for non-blocking operations
            self._active_threads = set()
            
            # Error types to retry
            self.retry_error_types = self.config['retry_error_types']
            
            # Map error type strings to actual exception classes
            # Include both built-in ConnectionError and requests.exceptions.ConnectionError
            import builtins
            self.error_class_map = {
                "ConnectionError": (builtins.ConnectionError, ConnectionError),
                "TimeoutError": TimeoutError,
                "URLError": URLError,
                "HTTPError": (HTTPError, RequestsHTTPError),
                "Timeout": Timeout,
                "HTTPException": HTTPException
            }
        
        def is_retryable_error(self, exception):
            """Check if an exception is retryable based on configuration"""
            for error_type in self.retry_error_types:
                error_class = self.error_class_map.get(error_type)
                if error_class:
                    if isinstance(error_class, tuple):
                        if isinstance(exception, error_class):
                            return True
                    elif isinstance(exception, error_class):
                        return True
            return False
        
        def retry(self, func, *args, success_callback=None, failure_callback=None, **kwargs):
            """Retry operation with exponential backoff - blocking mode"""
            with self._lock:
                max_attempts = self.config['retry_attempts']
                initial_delay = self.config['retry_delay']
                backoff_factor = self.config['backoff_factor']
                
                for attempt in range(max_attempts):
                    try:
                        start_time = time.time()
                        result = func(*args, **kwargs)
                        elapsed_time = time.time() - start_time
                        
                        logger.info(f"Operation succeeded on attempt {attempt + 1}/{max_attempts} in {elapsed_time:.3f}s")
                        
                        if success_callback:
                            success_callback(result)
                        
                        return result
                        
                    except Exception as e:
                        elapsed_time = time.time() - start_time
                        
                        if self.is_retryable_error(e):
                            logger.warning(f"Attempt {attempt + 1}/{max_attempts} failed in {elapsed_time:.3f}s: {type(e).__name__}: {e}")
                            
                            if attempt < max_attempts - 1:
                                # Calculate exponential backoff with jitter
                                delay = initial_delay * (backoff_factor ** attempt)
                                # Add jitter to prevent thundering herd problem
                                jitter = random.uniform(0, delay * 0.2)
                                total_delay = delay + jitter
                                
                                logger.info(f"Retrying in {total_delay:.1f}s...")
                                time.sleep(total_delay)
                                continue
                        else:
                            logger.error(f"Non-retryable error on attempt {attempt + 1}/{max_attempts} in {elapsed_time:.3f}s: {type(e).__name__}: {e}")
                        
                        logger.error(f"All {max_attempts} attempts failed")
                        
                        if failure_callback:
                            failure_callback(e)
                        
                        raise
        
        def retry_non_blocking(self, func, *args, success_callback=None, failure_callback=None, **kwargs):
            """Retry operation in non-blocking mode using threads"""
            def worker():
                """Thread worker function"""
                thread_id = threading.current_thread().ident
                try:
                    result = self.retry(func, *args, success_callback=success_callback, failure_callback=failure_callback, **kwargs)
                finally:
                    with self._lock:
                        self._active_threads.discard(thread_id)
            
            # Create and start new thread
            thread = threading.Thread(target=worker, daemon=True)
            with self._lock:
                thread.start()
                self._active_threads.add(thread.ident)
            
            return thread
        
        def retry_async(self, func, *args, success_callback=None, failure_callback=None, **kwargs):
            """Retry operation asynchronously with callback support"""
            result_queue = queue.Queue(maxsize=1)
            
            def internal_callback(result=None, error=None):
                if error:
                    result_queue.put((None, error))
                    if failure_callback:
                        failure_callback(error)
                else:
                    result_queue.put((result, None))
                    if success_callback:
                        success_callback(result)
            
            def worker():
                try:
                    result = self.retry(func, *args, **kwargs)
                    internal_callback(result=result)
                except Exception as e:
                    internal_callback(error=e)
            
            thread = threading.Thread(target=worker, daemon=True)
            thread.start()
            
            return result_queue
        
        def get_active_thread_count(self):
            """Get number of active retry threads"""
            with self._lock:
                return len(self._active_threads)
        
        def wait_for_all(self, timeout=None):
            """Wait for all active retry threads to complete"""
            start_time = time.time()
            
            while True:
                with self._lock:
                    if not self._active_threads:
                        return True
                
                if timeout:
                    elapsed = time.time() - start_time
                    if elapsed >= timeout:
                        return False
                
                time.sleep(0.1)  # Check every 100ms
    
    def _retry_operation(self, func, *args, **kwargs):
        """Retry operation with exponential backoff (backward compatibility)"""
        return self.retry_manager.retry(func, *args, **kwargs)
    
    def initialize_browser(self):
        """Initialize Playwright browser with support for multiple browsers"""
        try:
            playwright = sync_playwright().start()
            
            # Get browser configuration from config
            browser_type = self.config['advanced']['browser']
            browser_version = self.config['advanced']['browser_version']
            
            # Browser configuration for anti-detection
            browser_config = {
                "headless": False,  # Set to True for production
                "args": [
                    "--disable-blink-features=AutomationControlled",
                    "--disable-dev-shm-usage",
                    "--no-sandbox",
                    "--disable-setuid-sandbox"
                ],
                "ignore_default_args": ["--enable-automation"]
            }
            
            # Browser-specific configuration
            if browser_version != "stable":
                browser_config["channel"] = browser_version
            
            # Launch the appropriate browser
            if browser_type == "edge":
                logger.info(f"Initializing Microsoft Edge browser, version: {browser_version}")
                self.browser = playwright.chromium.launch(
                    channel="msedge" if browser_version == "stable" else f"msedge-{browser_version}",
                    **browser_config
                )
            elif browser_type == "firefox":
                logger.info(f"Initializing Mozilla Firefox browser, version: {browser_version}")
                self.browser = playwright.firefox.launch(
                    channel=browser_version if browser_version != "stable" else None,
                    **browser_config
                )
            else:  # Default to chromium
                logger.info(f"Initializing Chromium browser, version: {browser_version}")
                self.browser = playwright.chromium.launch(
                    channel=browser_version if browser_version != "stable" else None,
                    **browser_config
                )
            
            context = self.browser.new_context(
                user_agent=self._get_user_agent(),
                viewport={"width": 1920, "height": 1080}
            )
            
            # Add stealth script to avoid detection
            context.add_init_script("""
                // Standard anti-detection measures
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'languages', {get: () => ['zh-CN', 'zh', 'en']});
                Object.defineProperty(navigator, 'plugins', {get: () => [1, 2, 3]});
                Object.defineProperty(navigator, 'mimeTypes', {get: () => [1, 2, 3]});
                
                // Edge-specific fixes and compatibility
                if (navigator.userAgent.includes('Edg/')) {
                    // Ensure proper Edge browser detection
                    Object.defineProperty(navigator, 'userAgentData', {
                        get: () => ({
                            brands: [{brand: 'Microsoft Edge', version: '123'}],
                            mobile: false,
                            platform: 'Windows'
                        })
                    });
                }
            """)
            
            self.page = context.new_page()
            
            # Apply browser-specific fixes after page load
            def apply_browser_fixes():
                self.page.evaluate("""
                    // Polyfill for features that might be missing in Edge
                    if (!Array.prototype.at) {
                        Array.prototype.at = function(index) {
                            index = Math.trunc(index) || 0;
                            if (index < 0) index += this.length;
                            if (index < 0 || index >= this.length) return undefined;
                            return this[index];
                        };
                    }
                    
                    // Fix for Edge CSS rendering differences
                    const style = document.createElement('style');
                    style.textContent = `
                        /* Ensure consistent box-sizing across browsers */
                        * {
                            box-sizing: border-box !important;
                        }
                        /* Fix for Edge button styling issues */
                        button {
                            -webkit-appearance: none;
                            -moz-appearance: none;
                            appearance: none;
                        }
                    `;
                    document.head.appendChild(style);
                """)
            
            # Apply fixes immediately
            apply_browser_fixes()
            
            logger.info(f"{browser_type.capitalize()} browser initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            return False
    
    def login(self):
        """Automated login to Damai platform"""
        def login_operation():
            """Login operation wrapped for retry"""
            logger.info("Starting login process")
            self.page.goto("https://passport.damai.cn/login", timeout=60000)
            self._random_delay()
            
            # Choose login method
            login_config = self.config['login']
            
            if login_config['username'] and login_config['password']:
                # Username/password login
                logger.info("Using username/password login method")
                # Click password login tab
                self.page.click("//div[text()='密码登录']", timeout=10000)
                self._random_delay()
                
                # Enter username and password
                self.page.fill("#loginname", login_config['username'], timeout=10000)
                self._random_delay()
                self.page.fill("#password", login_config['password'], timeout=10000)
                self._random_delay()
                
                # Click login button
                self.page.click("#btn-submit", timeout=10000)
            
            elif login_config['phone_number']:
                # Phone number login
                logger.info("Using phone number login method")
                # Enter phone number
                self.page.fill("#phoneipt", login_config['phone_number'], timeout=10000)
                self._random_delay()
                
                # Click get verification code button
                self.page.click("#sendSmsCode", timeout=10000)
                self._random_delay()
                
                # Wait for user to enter SMS code
                logger.info("Please enter SMS verification code within 60 seconds...")
                time.sleep(60)
            
            else:
                logger.error("No login credentials provided")
                raise ValueError("No login credentials provided")
            
            # Check if login was successful by waiting for URL change
            self.page.wait_for_url("https://www.damai.cn/", timeout=60000)
            self._random_delay()
            logger.info("Login successful")
            return True
        
        def success_callback(result):
            logger.info("Login success callback: Login completed successfully")
        
        def failure_callback(error):
            logger.error(f"Login failure callback: {error}")
        
        try:
            return self.retry_manager.retry(
                login_operation,
                success_callback=success_callback,
                failure_callback=failure_callback
            )
        except Exception as e:
            logger.error(f"Login failed after all retry attempts: {e}")
            return False
    
    def monitor_ticket_availability(self):
        """Monitor ticket availability in real-time"""
        logger.info("Starting ticket availability monitoring")
        event_id = self.config['event']['event_id']
        refresh_interval = self.config['monitoring']['refresh_interval']
        max_monitoring_time = self.config['monitoring']['max_monitoring_time']
        
        start_time = time.time()
        
        def check_availability():
            """Check ticket availability wrapped for retry"""
            logger.info(f"Checking ticket availability for event {event_id}")
            
            # Navigate to event page
            self.page.goto(f"https://detail.damai.cn/item.htm?id={event_id}", timeout=30000)
            self._random_delay()
            
            # Check if tickets are available
            return self._is_ticket_available()
        
        def success_callback(result):
            if result:
                logger.info("Tickets are now available! Starting purchase process")
        
        def failure_callback(error):
            logger.error(f"Availability check failed: {error}")
        
        while time.time() - start_time < max_monitoring_time:
            try:
                is_available = self.retry_manager.retry(
                    check_availability,
                    success_callback=success_callback,
                    failure_callback=failure_callback
                )
                
                if is_available:
                    return True
                
                logger.info(f"Tickets not available yet. Checking again in {refresh_interval} seconds")
                time.sleep(refresh_interval)
                
            except Exception as e:
                logger.error(f"Monitoring loop error: {e}")
                self._random_delay()
        
        logger.error("Monitoring timed out")
        return False
    
    def _is_ticket_available(self):
        """Check if tickets are available"""
        try:
            # Check for buy button or available ticket indicators
            buy_button = self.page.query_selector("#buyNow" or "#J_buyBtn" or "//button[contains(text(), '立即购买')]")
            if buy_button and buy_button.is_visible():
                return True
            
            # Check if ticket options are available
            ticket_options = self.page.query_selector_all("//div[@class='select_right_list']//li")
            for option in ticket_options:
                if "disabled" not in option.get_attribute("class", default=""):
                    return True
            
            return False
        except Exception as e:
            logger.error(f"Error checking ticket availability: {e}")
            return False
    
    def select_tickets(self):
        """Select tickets based on user preferences"""
        try:
            logger.info("Starting ticket selection process")
            
            # Click buy button
            buy_button = self.page.query_selector("#buyNow" or "#J_buyBtn" or "//button[contains(text(), '立即购买')]")
            if buy_button and buy_button.is_visible():
                buy_button.click(timeout=10000)
                self._random_delay()
            
            # Wait for ticket selection page to load
            self.page.wait_for_selector("//div[@class='sku-content']", timeout=30000)
            self._random_delay()
            
            # Select ticket quantity
            self._select_ticket_quantity()
            
            # Select ticket type based on preferences
            self._select_ticket_type()
            
            logger.info("Ticket selection completed")
            return True
        except Exception as e:
            logger.error(f"Ticket selection failed: {e}")
            return False
    
    def _select_ticket_quantity(self):
        """Select ticket quantity"""
        quantity = self.config['event']['ticket_quantity']
        logger.info(f"Selecting {quantity} tickets")
        
        # Implement ticket quantity selection logic here
        # This will vary based on Damai's actual page structure
        self._random_delay()
    
    def _select_ticket_type(self):
        """Select ticket type based on user preferences"""
        preferences = self.config['ticket_preferences']
        logger.info(f"Selecting ticket type based on preferences: {preferences}")
        
        # Implement ticket type selection logic here
        # This will vary based on Damai's actual page structure
        self._random_delay()
    
    def checkout(self):
        """Automated checkout process"""
        try:
            logger.info("Starting checkout process")
            
            # Click submit order button
            submit_button = self.page.query_selector("//button[contains(text(), '提交订单')]" or "#submitOrder")
            if submit_button and submit_button.is_visible():
                submit_button.click(timeout=10000)
                self._random_delay()
            
            # Wait for payment page
            self.page.wait_for_selector("//div[@class='payment-wrapper']", timeout=30000)
            self._random_delay()
            
            # Select payment method
            payment_method = self.config['checkout']['payment_method']
            logger.info(f"Selecting payment method: {payment_method}")
            
            # Implement payment method selection logic here
            # This will vary based on Damai's actual page structure
            
            logger.info("Checkout process completed. Please complete payment manually if needed.")
            return True
        except Exception as e:
            logger.error(f"Checkout failed: {e}")
            return False
    
    def run(self):
        """Main execution flow"""
        try:
            logger.info("Starting Damai Ticket Purchasing System")
            
            # Initialize browser
            if not self.initialize_browser():
                return False
            
            # Login to Damai
            if not self.login():
                return False
            
            # Monitor ticket availability
            if not self.monitor_ticket_availability():
                return False
            
            # Select tickets
            if not self.select_tickets():
                return False
            
            # Checkout process
            if not self.checkout():
                return False
            
            logger.info("Ticket purchasing process completed successfully")
            return True
            
        except KeyboardInterrupt:
            logger.info("Program interrupted by user")
            return False
        except Exception as e:
            logger.error(f"Program encountered an error: {e}")
            return False
        finally:
            # Cleanup resources
            if self.browser:
                self.browser.close()
            logger.info("Program exited")

if __name__ == "__main__":
    # Create and run the ticket system
    ticket_system = DamaiTicketSystem()
    success = ticket_system.run()
    exit(0 if success else 1)
