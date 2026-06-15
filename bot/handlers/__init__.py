"""Handlers"""
from .start import router as start_router
from .url_handler import router as url_router
from .format_handler import router as format_router
from .cache_handler import router as cache_router
from .profile import router as profile_router
from .plans import router as plans_router
from .history import router as history_router
from .help import router as help_router
from .referral import router as referral_router
from .coin_conversion import router as coin_conversion_router
from .payment import router as payment_router
from .payment_rial import router as payment_rial_router
from .channels import router as channels_router
from .menu import router as menu_router
from .errors import router as errors_router
from .admin import bonus_coins_router

routers = [
    start_router,
    url_router,
    format_router,
    cache_router,
    profile_router,
    plans_router,
    history_router,
    help_router,
    referral_router,
    coin_conversion_router,
    payment_router,
    payment_rial_router,
    channels_router,
    bonus_coins_router,
    menu_router,
    errors_router,  # Must be last as it catches all messages
]

__all__ = ["routers"]
