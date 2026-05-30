"""
Phase 2 Integration Test Suite
Tests all Phase 2 components: Progress Bar, Coin System, Download Earning, Referral Flow
"""

import sys
import os
import asyncio
from pathlib import Path
from typing import List, Tuple
import traceback

PROJECT_ROOT = Path(__file__).parent
sys.path.insert(0, str(PROJECT_ROOT))

# Color codes for terminal output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    CYAN = '\033[96m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

class TestResult:
    def __init__(self):
        self.tests: List[Tuple[str, bool, str]] = []
        self.passed = 0
        self.failed = 0

    def add(self, name: str, success: bool, message: str = ""):
        self.tests.append((name, success, message))
        if success:
            self.passed += 1
        else:
            self.failed += 1

    def print_summary(self):
        print(f"\n{Colors.BOLD}{'='*70}{Colors.RESET}")
        print(f"{Colors.BOLD}PHASE 2 INTEGRATION TEST RESULTS{Colors.RESET}")
        print(f"{Colors.BOLD}{'='*70}{Colors.RESET}\n")

        for test_name, success, message in self.tests:
            icon = f"{Colors.GREEN}✅{Colors.RESET}" if success else f"{Colors.RED}❌{Colors.RESET}"
            print(f"{icon} {test_name}")
            if message:
                print(f"   {Colors.YELLOW}{message}{Colors.RESET}")

        total = self.passed + self.failed
        pct = (self.passed / total * 100) if total > 0 else 0
        print(f"\n{Colors.BOLD}Results: {Colors.GREEN}{self.passed}{Colors.RESET} passed, {Colors.RED}{self.failed}{Colors.RESET} failed out of {total} ({pct:.0f}%){Colors.RESET}")
        
        if self.failed == 0:
            print(f"\n{Colors.GREEN}{Colors.BOLD}🎉 ALL TESTS PASSED! 🎉{Colors.RESET}\n")
            return True
        else:
            print(f"\n{Colors.RED}{Colors.BOLD}⚠️ SOME TESTS FAILED{Colors.RESET}\n")
            return False

# ============================================================================
# TEST 1: Progress Bar Module
# ============================================================================
def test_progress_bar():
    """Test progress bar functionality"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Progress Bar ==={Colors.RESET}\n")
    
    try:
        from utils.progress import (
            ProgressBar, 
            generate_progress_message, 
            create_progress_bar,
            get_progress_lock,
            can_update_progress
        )
        results.add("Import progress utilities", True)
        
        # Test ProgressBar class
        pb = ProgressBar()
        results.add("Create ProgressBar instance", True)
        
        # Test progress message generation
        msg = generate_progress_message(
            phase="⬇️",
            downloaded=50 * 1024 * 1024,
            total=100 * 1024 * 1024,
            speed=1024 * 1024,
            time_elapsed=5
        )
        assert msg and "50%" in msg, "Progress message generation failed"
        results.add("Generate progress message", True, f"Message length: {len(msg)}")
        
        # Test progress lock
        lock = get_progress_lock(123)
        assert lock is not None, "Failed to get progress lock"
        results.add("Get progress lock", True)
        
        # Test throttle check
        can_update = can_update_progress(123)
        assert can_update, "Progress throttle check failed"
        results.add("Progress throttle check", True)
        
    except Exception as e:
        results.add(f"Progress bar test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 2: Coin Service
# ============================================================================
def test_coin_service():
    """Test coin transaction service"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Coin Service ==={Colors.RESET}\n")
    
    try:
        from services import CoinTransactionService
        results.add("Import CoinTransactionService", True)
        
        # Check if class has all required methods
        required_methods = [
            'add_coins',
            'spend_coins',
            'get_user_balance',
            'get_user_transactions',
            'get_transaction_stats',
            'bonus_coins'
        ]
        
        for method in required_methods:
            assert hasattr(CoinTransactionService, method), f"Missing method: {method}"
        
        results.add("CoinTransactionService has all methods", True, f"{len(required_methods)} methods verified")
        
    except Exception as e:
        results.add("Coin service test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 3: Referral Service
# ============================================================================
def test_referral_service():
    """Test referral service"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Referral Service ==={Colors.RESET}\n")
    
    try:
        from services import ReferralService
        results.add("Import ReferralService", True)
        
        # Check if class has all required methods
        required_methods = [
            'create_referral',
            'mark_referral_complete',
            'get_user_referrals',
            'get_user_referral_count',
            'get_referral_by_code',
            'is_referral_valid'
        ]
        
        for method in required_methods:
            assert hasattr(ReferralService, method), f"Missing method: {method}"
        
        results.add("ReferralService has all methods", True, f"{len(required_methods)} methods verified")
        
    except Exception as e:
        results.add("Referral service test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 4: Download Handler Integration
# ============================================================================
def test_download_handler():
    """Test download handler with coin earning"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Download Handler ==={Colors.RESET}\n")
    
    try:
        from bot.handlers.download import award_download_coins
        results.add("Import award_download_coins function", True)
        
        # Verify function signature
        import inspect
        sig = inspect.signature(award_download_coins)
        params = list(sig.parameters.keys())
        
        expected_params = ['user_id', 'file_size_bytes', 'session']
        for param in expected_params:
            assert param in params, f"Missing parameter: {param}"
        
        results.add("award_download_coins has correct signature", True, f"Parameters: {params}")
        
    except Exception as e:
        results.add("Download handler test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 5: Start Handler Integration
# ============================================================================
def test_start_handler():
    """Test start handler with referral integration"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Start Handler ==={Colors.RESET}\n")
    
    try:
        from bot.handlers.start import router, cmd_start
        results.add("Import start handler router", True)
        
        # Verify function exists
        import inspect
        sig = inspect.signature(cmd_start)
        params = list(sig.parameters.keys())
        
        # Should have 'message' and 'session' parameters
        assert 'message' in params, "Missing 'message' parameter"
        assert 'session' in params, "Missing 'session' parameter"
        
        results.add("cmd_start has correct parameters", True, f"Parameters: {params}")
        
    except Exception as e:
        results.add("Start handler test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 6: Coin Conversion Handler
# ============================================================================
def test_coin_conversion_handler():
    """Test coin conversion handler"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Coin Conversion Handler ==={Colors.RESET}\n")
    
    try:
        from bot.handlers.coin_conversion import router
        results.add("Import coin_conversion handler router", True)
        
        # Verify router is properly configured
        assert router is not None, "Router is None"
        assert hasattr(router, '_handlers'), "Router has no handlers"
        
        results.add("Coin conversion router is properly configured", True)
        
    except Exception as e:
        results.add("Coin conversion handler test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 7: Admin Bonus Coins Handler
# ============================================================================
def test_admin_bonus_handler():
    """Test admin bonus coins handler"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Admin Bonus Handler ==={Colors.RESET}\n")
    
    try:
        from bot.handlers.admin.bonus_coins import router as bonus_router
        results.add("Import admin bonus_coins router", True)
        
        # Verify router is properly configured
        assert bonus_router is not None, "Router is None"
        assert hasattr(bonus_router, '_handlers'), "Router has no handlers"
        
        results.add("Admin bonus router is properly configured", True)
        
    except Exception as e:
        results.add("Admin bonus handler test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 8: Database Models
# ============================================================================
def test_database_models():
    """Test database models for coin system"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Database Models ==={Colors.RESET}\n")
    
    try:
        from database.models import User, CoinTransaction, Referral
        results.add("Import User model", True)
        results.add("Import CoinTransaction model", True)
        results.add("Import Referral model", True)
        
        # Verify User model has coin fields
        assert hasattr(User, 'total_coins'), "User model missing total_coins field"
        assert hasattr(User, 'referral_code'), "User model missing referral_code field"
        assert hasattr(User, 'referred_by'), "User model missing referred_by field"
        
        results.add("User model has coin/referral fields", True)
        
        # Verify CoinTransaction model
        assert hasattr(CoinTransaction, 'user_id'), "CoinTransaction missing user_id"
        assert hasattr(CoinTransaction, 'amount'), "CoinTransaction missing amount"
        assert hasattr(CoinTransaction, 'transaction_type'), "CoinTransaction missing transaction_type"
        
        results.add("CoinTransaction model has required fields", True)
        
        # Verify Referral model
        assert hasattr(Referral, 'referrer_id'), "Referral missing referrer_id"
        assert hasattr(Referral, 'referred_user_id'), "Referral missing referred_user_id"
        
        results.add("Referral model has required fields", True)
        
    except Exception as e:
        results.add("Database models test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 9: Handler Registration
# ============================================================================
def test_handler_registration():
    """Test that all handlers are properly registered"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Handler Registration ==={Colors.RESET}\n")
    
    try:
        from bot.handlers import routers
        results.add("Import handlers routers list", True)
        
        # Check that all required routers are registered
        router_names = []
        for router in routers:
            if hasattr(router, 'description'):
                router_names.append(router.description)
        
        results.add(f"Handlers registered: {len(routers)} routers", True, f"Routers loaded successfully")
        
        # Verify specific routers
        from bot.handlers import (
            start_router,
            download_router,
            coin_conversion_router,
        )
        results.add("start_router imported", True)
        results.add("download_router imported", True)
        results.add("coin_conversion_router imported", True)
        
    except Exception as e:
        results.add("Handler registration test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# TEST 10: Services Export
# ============================================================================
def test_services_export():
    """Test that all services are properly exported"""
    results = TestResult()
    print(f"\n{Colors.CYAN}{Colors.BOLD}=== Testing Services Export ==={Colors.RESET}\n")
    
    try:
        from services import (
            CoinTransactionService,
            ReferralService,
            DownloadService,
            UserService
        )
        results.add("CoinTransactionService exported", True)
        results.add("ReferralService exported", True)
        results.add("DownloadService exported", True)
        results.add("UserService exported", True)
        
    except Exception as e:
        results.add("Services export test", False, str(e))
        traceback.print_exc()
    
    return results

# ============================================================================
# MAIN TEST RUNNER
# ============================================================================
def run_all_tests():
    """Run all integration tests"""
    print(f"\n{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}PHASE 2 INTEGRATION TEST SUITE{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.CYAN}{'='*70}{Colors.RESET}\n")
    
    all_results = []
    
    # Run all test groups
    all_results.append(test_progress_bar())
    all_results.append(test_coin_service())
    all_results.append(test_referral_service())
    all_results.append(test_download_handler())
    all_results.append(test_start_handler())
    all_results.append(test_coin_conversion_handler())
    all_results.append(test_admin_bonus_handler())
    all_results.append(test_database_models())
    all_results.append(test_handler_registration())
    all_results.append(test_services_export())
    
    # Combine all results
    combined = TestResult()
    for result in all_results:
        for test_name, success, message in result.tests:
            combined.add(test_name, success, message)
    
    # Print final summary
    return combined.print_summary()

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
