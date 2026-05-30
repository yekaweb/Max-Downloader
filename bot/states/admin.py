"""Admin state machine"""
from aiogram.fsm.state import StatesGroup, State


class AdminStates(StatesGroup):
    dashboard = State()
    user_search = State()
    broadcast_message = State()
    plan_edit = State()
    channel_management = State()


__all__ = ["AdminStates"]
