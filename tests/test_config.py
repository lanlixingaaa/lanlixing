#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for configuration handling
"""

import os
import yaml
import pytest
from damai_ticket import DamaiTicketSystem

class TestConfig:
    """Test configuration loading and parsing"""
    
    def test_config_loading(self):
        """Test that configuration loads successfully"""
        system = DamaiTicketSystem()
        assert system.config is not None
        assert isinstance(system.config, dict)
    
    def test_config_structure(self):
        """Test that configuration has expected structure"""
        system = DamaiTicketSystem()
        
        # Check main sections exist
        assert 'login' in system.config
        assert 'event' in system.config
        assert 'ticket_preferences' in system.config
        assert 'monitoring' in system.config
        assert 'anti_detect' in system.config
        assert 'checkout' in system.config
        
        # Check required fields exist
        assert 'username' in system.config['login']
        assert 'password' in system.config['login']
        assert 'event_id' in system.config['event']
        assert 'ticket_quantity' in system.config['event']
    
    def test_invalid_config_file(self, tmp_path):
        """Test handling of invalid configuration file"""
        # Create invalid YAML file
        invalid_config = tmp_path / "invalid_config.yaml"
        invalid_config.write_text("invalid: yaml: content: }")
        
        with pytest.raises(Exception):
            DamaiTicketSystem(str(invalid_config))
    
    def test_missing_config_file(self):
        """Test handling of missing configuration file"""
        with pytest.raises(Exception):
            DamaiTicketSystem("missing_config.yaml")
    
    def test_config_default_values(self):
        """Test that default configuration values are set correctly"""
        system = DamaiTicketSystem()
        
        assert system.config['monitoring']['refresh_interval'] == 5
        assert system.config['monitoring']['max_monitoring_time'] == 3600
        assert system.config['advanced']['retry_attempts'] == 5
    
    def test_custom_config_values(self, tmp_path):
        """Test that custom configuration values are loaded correctly"""
        # Create custom config
        custom_config = {
            'login': {
                'username': 'test_user',
                'password': 'test_pass'
            },
            'event': {
                'event_id': '123456',
                'ticket_quantity': 3
            },
            'monitoring': {
                'refresh_interval': 10,
                'max_monitoring_time': 1800
            }
        }
        
        custom_config_path = tmp_path / "custom_config.yaml"
        with open(custom_config_path, 'w', encoding='utf-8') as f:
            yaml.dump(custom_config, f)
        
        system = DamaiTicketSystem(str(custom_config_path))
        assert system.config['login']['username'] == 'test_user'
        assert system.config['event']['ticket_quantity'] == 3
        assert system.config['monitoring']['refresh_interval'] == 10
