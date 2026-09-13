"""
Unit tests for Titan Mesh services:
  - PoTokenService
  - CobaltService
  - WaterfallDownloadService
  - AccountPoolService (VIP calculation)
  - AiDubbingService
"""

import pytest
from services.potoken_service import PoTokenService
from services.cobalt_service import CobaltService
from services.account_pool_service import VIP_TIERS, AccountPoolService


def test_potoken_service_init_and_injection():
    service = PoTokenService(ttl_seconds=3600)
    assert not service.is_token_valid()
    
    # Simulate cached tokens
    service._cached_po_token = "test_token_123"
    service._cached_visitor_data = "test_visitor_456"
    import time
    service._last_generated = time.time()
    
    assert service.is_token_valid()
    
    opts = {}
    updated = service.inject_into_ydl_opts(opts)
    assert updated["extractor_args"]["youtube"]["po_token"] == ["web+test_token_123"]
    assert updated["extractor_args"]["youtube"]["visitor_data"] == ["test_visitor_456"]


def test_cobalt_service_instances():
    service = CobaltService()
    assert len(service.instances) >= 2
    assert "https://api.cobalt.tools" in service.instances


def test_vip_tiers_calculation():
    # Helper without DB session to test pure math
    class DummyPool:
        calculate_vip_tier = AccountPoolService.calculate_vip_tier

    dummy = DummyPool()
    assert dummy.calculate_vip_tier(0) is None
    assert dummy.calculate_vip_tier(1) is None
    
    tier_2 = dummy.calculate_vip_tier(2)
    assert tier_2["title"] == VIP_TIERS["sepahbod"]["title"]
    assert tier_2["daily_limit_gb"] == 50
    
    tier_3 = dummy.calculate_vip_tier(3)
    assert tier_3["title"] == VIP_TIERS["esfandiar"]["title"]
    assert tier_3["daily_limit_gb"] == 100
    
    tier_5 = dummy.calculate_vip_tier(5)
    assert tier_5["title"] == VIP_TIERS["rostam"]["title"]
    assert tier_5["daily_limit_gb"] == 999999


def test_instagram_service_detection_and_session(tmp_path, monkeypatch):
    from services.instagram_service import InstagramService
    service = InstagramService()
    
    # Test URL detection
    assert service.is_instagram_url("https://www.instagram.com/reel/DdNM4okJi4P/")
    assert service.is_instagram_url("https://instagram.com/p/C123456/")
    assert not service.is_instagram_url("https://www.youtube.com/watch?v=12345")
    
    # Test session setup
    session_file = tmp_path / "instagram_session.json"
    cookie_file = tmp_path / "cookies.txt"
    monkeypatch.setattr("services.instagram_service.SESSION_FILE", session_file)
    monkeypatch.setattr("services.instagram_service.COOKIE_FILE", cookie_file)
    
    assert service.set_session_id("test_session_id_999", "12345678")
    assert service.has_active_session()
    assert cookie_file.exists()
    content = cookie_file.read_text()
    assert "test_session_id_999" in content
    assert "instagram.com" in content

