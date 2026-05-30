"""Unit tests for utility functions"""
import pytest
from utils.progress import (
    ProgressBar,
    create_progress_bar,
    generate_progress_message,
    can_update_progress
)


@pytest.mark.unit
class TestProgressBar:
    """Test progress bar generation"""
    
    def test_progress_bar_creation(self):
        """Test creating a progress bar"""
        pb = ProgressBar()
        assert pb.bar_style == "gradient"
        assert pb.bar_length == 20
    
    def test_progress_bar_generation(self):
        """Test progress bar output"""
        pb = ProgressBar()
        output = pb.generate(
            current=500,
            total=1000,
            speed=50.0,
            eta_seconds=10,
            title="Test Video"
        )
        
        assert output is not None
        assert "Test Video" in output
        assert "50%" in output or "5.0" in output
    
    def test_compact_progress_bar(self):
        """Test compact progress bar"""
        pb = ProgressBar()
        output = pb.generate_compact(
            current=750,
            total=1000,
            speed=75.0
        )
        
        assert output is not None
        assert "%" in output
    
    def test_detailed_progress_bar(self):
        """Test detailed progress bar"""
        pb = ProgressBar()
        output = pb.generate_detailed(
            current=500,
            total=1000,
            speed=50.0,
            eta_seconds=10,
            elapsed_seconds=10,
            title="Test"
        )
        
        assert output is not None
        assert "Progress" in output or "500" in output


@pytest.mark.unit
class TestProgressMessage:
    """Test progress message generation"""
    
    def test_generate_progress_message(self, mock_progress_data):
        """Test generating progress message"""
        message = generate_progress_message(**mock_progress_data)
        
        assert message is not None
        assert mock_progress_data["title"] in message
        assert "50" in message or "50.0" in message
    
    def test_progress_message_with_queue(self, mock_progress_data):
        """Test progress message with queue position"""
        mock_progress_data["queue_position"] = 3
        message = generate_progress_message(**mock_progress_data)
        
        assert message is not None
        assert "موقعیت" in message or "queue" in message.lower() or "3" in message
    
    def test_progress_message_phases(self):
        """Test progress message for different phases"""
        phases = ["download", "upload", "processing"]
        
        for phase in phases:
            message = generate_progress_message(
                title="Test",
                progress_percent=50.0,
                downloaded_mb=50.0,
                total_mb=100.0,
                speed_mbps=5.0,
                eta_seconds=10,
                phase=phase
            )
            
            assert message is not None


@pytest.mark.unit
@pytest.mark.asyncio
class TestProgressThrottling:
    """Test progress throttling"""
    
    async def test_can_update_progress_true_on_first_call(self):
        """Test that first update is allowed"""
        result = await can_update_progress(user_id=123, throttle_seconds=3.0)
        assert result is True
    
    async def test_can_update_progress_false_on_quick_call(self):
        """Test that quick successive calls are throttled"""
        # First update
        await can_update_progress(user_id=456, throttle_seconds=3.0)
        
        # Second update should be throttled
        result = await can_update_progress(user_id=456, throttle_seconds=3.0)
        assert result is False
    
    @pytest.mark.slow
    async def test_can_update_progress_true_after_delay(self):
        """Test that update is allowed after throttle delay"""
        import asyncio
        
        user_id = 789
        
        # First update
        await can_update_progress(user_id=user_id, throttle_seconds=1.0)
        
        # Wait for throttle to expire
        await asyncio.sleep(1.1)
        
        # Second update should be allowed
        result = await can_update_progress(user_id=user_id, throttle_seconds=1.0)
        assert result is True
