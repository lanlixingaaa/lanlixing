#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tests for the main program flow and end-to-end functionality
"""

import pytest
from unittest.mock import MagicMock, patch
from damai_ticket import DamaiTicketSystem

class TestMainFlow:
    """Test the main program flow"""
    
    def test_main_flow_success(self):
        """Test the complete main flow with all components mocked successfully"""
        system = DamaiTicketSystem()
        
        # Mock all major components to return success
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', return_value=True):
                with patch.object(system, 'monitor_ticket_availability', return_value=True):
                    with patch.object(system, 'select_tickets', return_value=True):
                        with patch.object(system, 'checkout', return_value=True):
                            # Call the main run method
                            result = system.run()
                            assert result is True
    
    def test_main_flow_browser_failure(self):
        """Test main flow when browser initialization fails"""
        system = DamaiTicketSystem()
        
        # Mock browser initialization to fail
        with patch.object(system, 'initialize_browser', return_value=False):
            # Call the main run method
            result = system.run()
            assert result is False
    
    def test_main_flow_login_failure(self):
        """Test main flow when login fails"""
        system = DamaiTicketSystem()
        
        # Mock browser initialization to succeed but login to fail
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', return_value=False):
                # Call the main run method
                result = system.run()
                assert result is False
    
    def test_main_flow_monitoring_failure(self):
        """Test main flow when ticket monitoring fails"""
        system = DamaiTicketSystem()
        
        # Mock browser and login to succeed but monitoring to fail
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', return_value=True):
                with patch.object(system, 'monitor_ticket_availability', return_value=False):
                    # Call the main run method
                    result = system.run()
                    assert result is False
    
    def test_main_flow_selection_failure(self):
        """Test main flow when ticket selection fails"""
        system = DamaiTicketSystem()
        
        # Mock browser, login, and monitoring to succeed but selection to fail
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', return_value=True):
                with patch.object(system, 'monitor_ticket_availability', return_value=True):
                    with patch.object(system, 'select_tickets', return_value=False):
                        # Call the main run method
                        result = system.run()
                        assert result is False
    
    def test_main_flow_checkout_failure(self):
        """Test main flow when checkout fails"""
        system = DamaiTicketSystem()
        
        # Mock everything to succeed except checkout
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', return_value=True):
                with patch.object(system, 'monitor_ticket_availability', return_value=True):
                    with patch.object(system, 'select_tickets', return_value=True):
                        with patch.object(system, 'checkout', return_value=False):
                            # Call the main run method
                            result = system.run()
                            assert result is False
    
    def test_main_flow_keyboard_interrupt(self):
        """Test main flow when keyboard interrupt is received"""
        system = DamaiTicketSystem()
        
        # Mock browser initialization to succeed, then raise KeyboardInterrupt during login
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', side_effect=KeyboardInterrupt()):
                # Call the main run method
                result = system.run()
                assert result is False
    
    def test_main_flow_exception_handling(self):
        """Test main flow exception handling"""
        system = DamaiTicketSystem()
        
        # Mock browser initialization to succeed, then raise exception during login
        with patch.object(system, 'initialize_browser', return_value=True):
            with patch.object(system, 'login', side_effect=Exception("Test exception")):
                # Call the main run method
                result = system.run()
                assert result is False
    
    def test_monitoring_flow(self):
        """Test the monitoring flow with mocked page"""
        system = DamaiTicketSystem()
        
        # Setup configuration
        system.config['event']['event_id'] = '123456'
        system.config['monitoring']['refresh_interval'] = 1
        system.config['monitoring']['max_monitoring_time'] = 5
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods
        mock_page.goto = MagicMock()
        
        # Mock _is_ticket_available to return False initially, then True
        availability_calls = [False, False, True]
        
        def mock_is_ticket_available():
            if availability_calls:
                return availability_calls.pop(0)
            return False
        
        with patch.object(system, '_is_ticket_available', side_effect=mock_is_ticket_available):
            with patch.object(system, '_random_delay', return_value=None):
                # Mock time.sleep to speed up test
                with patch('damai_ticket.time.sleep', return_value=None):
                    result = system.monitor_ticket_availability()
                    assert result is True
                    assert mock_page.goto.call_count > 0
    
    def test_monitoring_timeout(self):
        """Test monitoring timeout scenario"""
        system = DamaiTicketSystem()
        
        # Setup configuration with short timeout
        system.config['event']['event_id'] = '123456'
        system.config['monitoring']['refresh_interval'] = 1
        system.config['monitoring']['max_monitoring_time'] = 3
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods
        mock_page.goto = MagicMock()
        
        # Mock _is_ticket_available to always return False
        with patch.object(system, '_is_ticket_available', return_value=False):
            with patch.object(system, '_random_delay', return_value=None):
                # Mock time.sleep to speed up test
                with patch('damai_ticket.time.sleep', return_value=None):
                    result = system.monitor_ticket_availability()
                    assert result is False
                    assert mock_page.goto.call_count > 0
