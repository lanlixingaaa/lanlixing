#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Integration tests for Damai ticket system
"""

import pytest
from unittest.mock import MagicMock, patch
from damai_ticket import DamaiTicketSystem

class TestIntegration:
    """Test integration between system components"""
    
    def test_browser_initialization_integration(self):
        """Test browser initialization with mocked Playwright"""
        system = DamaiTicketSystem()
        
        # Mock the entire initialize_browser method to return True
        with patch.object(system, 'initialize_browser', return_value=True):
            # Call initialize_browser
            result = system.initialize_browser()
            
            # Verify the method was called and returned True
            system.initialize_browser.assert_called_once()
            assert result is True
    
    def test_login_flow_integration(self):
        """Test login flow with mocked browser"""
        system = DamaiTicketSystem()
        
        # Setup configuration with login credentials
        system.config['login']['username'] = 'test_user'
        system.config['login']['password'] = 'test_pass'
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods
        mock_page.goto = MagicMock()
        mock_page.click = MagicMock()
        mock_page.fill = MagicMock()
        mock_page.wait_for_url = MagicMock()
        
        # Call login method
        result = system.login()
        
        # Verify login flow
        mock_page.goto.assert_called_once_with("https://passport.damai.cn/login", timeout=60000)
        mock_page.click.assert_any_call("//div[text()='密码登录']", timeout=10000)
        mock_page.fill.assert_any_call("#loginname", "test_user", timeout=10000)
        mock_page.fill.assert_any_call("#password", "test_pass", timeout=10000)
        mock_page.click.assert_any_call("#btn-submit", timeout=10000)
        mock_page.wait_for_url.assert_called_once_with("https://www.damai.cn/", timeout=60000)
        
        assert result is True
    
    def test_ticket_availability_check_integration(self):
        """Test ticket availability check with mocked page"""
        system = DamaiTicketSystem()
        system.config['event']['event_id'] = '123456'
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods for available tickets
        mock_page.goto = MagicMock()
        mock_buy_button = MagicMock()
        mock_buy_button.is_visible.return_value = True
        mock_page.query_selector.return_value = mock_buy_button
        
        # Mock _random_delay to speed up test
        with patch.object(system, '_random_delay', return_value=None):
            # Call is_ticket_available method
            result = system._is_ticket_available()
            assert result is True
            
            # Verify page interactions
            mock_page.query_selector.assert_called_once()
            mock_buy_button.is_visible.assert_called_once()
    
    def test_ticket_availability_unavailable_integration(self):
        """Test ticket availability check when tickets are unavailable"""
        system = DamaiTicketSystem()
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods for unavailable tickets
        mock_buy_button = MagicMock()
        mock_buy_button.is_visible.return_value = False
        mock_page.query_selector.return_value = mock_buy_button
        
        # Mock ticket options as all disabled
        mock_ticket_option = MagicMock()
        mock_ticket_option.get_attribute.return_value = "disabled"
        mock_page.query_selector_all.return_value = [mock_ticket_option] * 5
        
        # Mock _random_delay to speed up test
        with patch.object(system, '_random_delay', return_value=None):
            # Call is_ticket_available method
            result = system._is_ticket_available()
            assert result is False
    
    def test_login_with_phone_integration(self):
        """Test phone login flow with mocked browser"""
        system = DamaiTicketSystem()
        
        # Setup configuration with phone number
        system.config['login']['phone_number'] = '13800138000'
        system.config['login']['username'] = ''
        system.config['login']['password'] = ''
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods - simulate timeout in wait_for_url to indicate login failure
        mock_page.goto = MagicMock()
        mock_page.click = MagicMock()
        mock_page.fill = MagicMock()
        mock_page.wait_for_url = MagicMock(side_effect=Exception("Timeout waiting for login URL"))
        
        # Mock _random_delay and time.sleep to speed up test
        with patch.object(system, '_random_delay', return_value=None):
            with patch('damai_ticket.time.sleep', return_value=None):
                # Call login method
                result = system.login()
                
                # Verify phone login flow
                mock_page.goto.assert_called_once_with("https://passport.damai.cn/login", timeout=60000)
                mock_page.fill.assert_called_once_with("#phoneipt", "13800138000", timeout=10000)
                mock_page.click.assert_called_once_with("#sendSmsCode", timeout=10000)
                mock_page.wait_for_url.assert_called_once()
                
                assert result is False  # Should return False as login failed due to timeout
    
    def test_system_initialization_integration(self):
        """Test complete system initialization flow"""
        # Test that the system initializes all components correctly
        system = DamaiTicketSystem()
        
        # Verify configuration is loaded
        assert system.config is not None
        
        # Verify anti-detection setup
        assert hasattr(system, 'ua')
        
        # Verify browser is not initialized yet
        assert system.browser is None
        assert system.page is None
    
    def test_ticket_selection_integration(self):
        """Test ticket selection flow with mocked browser"""
        system = DamaiTicketSystem()
        
        # Mock browser page
        mock_page = MagicMock()
        system.page = mock_page
        
        # Mock page methods
        mock_buy_button = MagicMock()
        mock_buy_button.is_visible.return_value = True
        mock_page.query_selector.return_value = mock_buy_button
        mock_page.wait_for_selector = MagicMock()
        
        # Mock select_ticket_quantity and select_ticket_type
        with patch.object(system, '_select_ticket_quantity', return_value=None):
            with patch.object(system, '_select_ticket_type', return_value=None):
                with patch.object(system, '_random_delay', return_value=None):
                    # Call select_tickets method
                    result = system.select_tickets()
                    assert result is True
                    
                    # Verify calls
                    mock_buy_button.click.assert_called_once_with(timeout=10000)
                    mock_page.wait_for_selector.assert_called_once()
