#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Unit tests for anti-detection mechanisms
"""

import pytest
from damai_ticket import DamaiTicketSystem

class TestAntiDetect:
    """Test anti-detection features"""
    
    def test_random_delay_generation(self):
        """Test that random delays are generated within configured range"""
        system = DamaiTicketSystem()
        
        # Test multiple times to ensure consistency
        for _ in range(10):
            delay_min = system.config['anti_detect']['random_delay_min']
            delay_max = system.config['anti_detect']['random_delay_max']
            
            # Monkey patch time.sleep to capture the delay
            captured_delay = None
            original_sleep = system._random_delay.__globals__['time'].sleep
            
            def mock_sleep(delay):
                nonlocal captured_delay
                captured_delay = delay
            
            system._random_delay.__globals__['time'].sleep = mock_sleep
            
            try:
                system._random_delay()
                assert captured_delay is not None
                assert delay_min <= captured_delay <= delay_max
            finally:
                # Restore original sleep function
                system._random_delay.__globals__['time'].sleep = original_sleep
    
    def test_user_agent_generation(self):
        """Test that user agents are generated correctly"""
        system = DamaiTicketSystem()
        
        # Test with user-agent rotation enabled
        system.config['anti_detect']['rotate_user_agent'] = True
        user_agents = set()
        
        for _ in range(10):
            user_agent = system._get_user_agent()
            assert isinstance(user_agent, str)
            assert len(user_agent) > 0
            user_agents.add(user_agent)
        
        # Ensure we're getting different user agents
        assert len(user_agents) > 1
        
        # Test with user-agent rotation disabled
        system.config['anti_detect']['rotate_user_agent'] = False
        fixed_user_agent = system._get_user_agent()
        assert isinstance(fixed_user_agent, str)
        assert len(fixed_user_agent) > 0
        
        # Ensure we get the same user agent every time
        for _ in range(5):
            assert system._get_user_agent() == fixed_user_agent
    
    def test_retry_operation_success(self):
        """Test that retry operation works correctly for successful function calls"""
        system = DamaiTicketSystem()
        
        # Mock function that always succeeds
        def successful_func():
            return "success"
        
        result = system._retry_operation(successful_func)
        assert result == "success"
    
    def test_retry_operation_failure(self):
        """Test that retry operation handles repeated failures"""
        system = DamaiTicketSystem()
        
        # Mock function that always fails
        def failing_func():
            raise Exception("Test failure")
        
        with pytest.raises(Exception, match="Test failure"):
            system._retry_operation(failing_func)
    
    def test_retry_operation_eventual_success(self):
        """Test that retry operation succeeds after multiple attempts"""
        system = DamaiTicketSystem()
        
        # Mock function that fails n times before succeeding
        attempt_count = 0
        max_failures = 2
        
        def eventual_success_func():
            nonlocal attempt_count
            attempt_count += 1
            if attempt_count <= max_failures:
                raise Exception(f"Attempt {attempt_count} failed")
            return "eventual success"
        
        result = system._retry_operation(eventual_success_func)
        assert result == "eventual success"
        assert attempt_count == max_failures + 1
    
    def test_retry_operation_with_arguments(self):
        """Test that retry operation passes arguments correctly"""
        system = DamaiTicketSystem()
        
        # Mock function that requires arguments
        def func_with_args(arg1, arg2, kwarg1=None, kwarg2=None):
            return f"arg1={arg1}, arg2={arg2}, kwarg1={kwarg1}, kwarg2={kwarg2}"
        
        result = system._retry_operation(
            func_with_args,
            "value1",
            "value2",
            kwarg1="kwvalue1",
            kwarg2="kwvalue2"
        )
        
        assert result == "arg1=value1, arg2=value2, kwarg1=kwvalue1, kwarg2=kwvalue2"
