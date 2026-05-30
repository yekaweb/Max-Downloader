"""Payment state machine"""
from aiogram.fsm.state import StatesGroup, State


class PaymentStates(StatesGroup):
    selecting_plan = State()
    confirming_payment = State()
    processing_payment = State()
    payment_success = State()
    payment_failed = State()


__all__ = ["PaymentStates"]
