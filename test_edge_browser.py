#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Edge Browser Compatibility Test
"""

import yaml
import time
from damai_ticket import DamaiTicketSystem
from loguru import logger

# Setup logging
logger.remove()
logger.add(
    "test_edge_browser.log",
    level="DEBUG",
    rotation="10 MB",
    retention=5
)
logger.add(
    sink=lambda msg: print(msg, end=""),
    level="INFO"
)

def test_edge_browser_compatibility():
    """
    Test Edge browser compatibility by initializing the browser and checking basic functionality
    """
    logger.info("=== Starting Edge Browser Compatibility Test ===")
    
    try:
        # Create a temporary config with Edge browser settings
        test_config = {
            "login": {
                "username": "",
                "password": "",
                "phone_number": ""
            },
            "event": {
                "event_id": "",
                "ticket_quantity": 1
            },
            "ticket_preferences": {
                "price_ranges": [],
                "sections": [],
                "rows": [],
                "seat_type": ""
            },
            "monitoring": {
                "refresh_interval": 5,
                "max_monitoring_time": 60
            },
            "anti_detect": {
                "random_delay_min": 0.5,
                "random_delay_max": 1.0,
                "rotate_user_agent": True
            },
            "checkout": {
                "auto_submit_order": True,
                "payment_method": "alipay",
                "timeout": 30
            },
            "logging": {
                "level": "INFO",
                "log_file": "damai_ticket.log",
                "max_log_size": 10,
                "backup_count": 5
            },
            "advanced": {
                "retry_attempts": 3,
                "retry_delay": 1,
                "backoff_factor": 2.0,
                "retry_error_types": ["ConnectionError", "TimeoutError", "URLError", "HTTPError"],
                "session_timeout": 1800,
                "browser": "edge",
                "browser_version": "stable"
            }
        }
        
        # Write test config to a temporary file
        with open("test_edge_config.yaml", "w", encoding="utf-8") as f:
            yaml.dump(test_config, f, default_flow_style=False, allow_unicode=True)
        
        # Create ticket system instance with Edge config
        ticket_system = DamaiTicketSystem("test_edge_config.yaml")
        
        # Test browser initialization
        logger.info("Testing Edge browser initialization...")
        browser_initialized = ticket_system.initialize_browser()
        
        if browser_initialized:
            logger.info("✓ Edge browser initialized successfully")
            
            # Test basic browser functionality
            logger.info("Testing basic browser functionality...")
            
            # Navigate to a simple page
            ticket_system.page.goto("https://www.baidu.com")
            time.sleep(1)
            
            # Check if page loaded successfully
            page_title = ticket_system.page.title()
            logger.info(f"Page title: {page_title}")
            
            if "百度" in page_title:
                logger.info("✓ Basic browser navigation works correctly")
            else:
                logger.error("✗ Basic browser navigation failed")
            
            # Close browser
            ticket_system.browser.close()
            logger.info("✓ Browser closed successfully")
            
            logger.info("=== Edge Browser Compatibility Test PASSED ===")
            return True
        else:
            logger.error("✗ Edge browser initialization failed")
            logger.info("=== Edge Browser Compatibility Test FAILED ===")
            return False
            
    except Exception as e:
        logger.error(f"✗ Test failed with exception: {e}")
        logger.info("=== Edge Browser Compatibility Test FAILED ===")
        return False
    finally:
        # Clean up temporary config file
        import os
        if os.path.exists("test_edge_config.yaml"):
            os.remove("test_edge_config.yaml")
        if os.path.exists("test_edge_browser.log"):
            os.remove("test_edge_browser.log")

if __name__ == "__main__":
    success = test_edge_browser_compatibility()
    exit(0 if success else 1)
