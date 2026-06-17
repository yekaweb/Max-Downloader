"""Force-join channel handlers - require users to join channels"""

from aiogram import Router, F, types
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database.models import Channel, User
import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("channels"))
async def cmd_channels(
    message: Message,
    state: FSMContext,
    session: AsyncSession
):
    """
    /channels - Admin command to manage force-join channels
    """
    # Check if admin (in production, use admin filter)
    if message.from_user.id != 123456789:  # Replace with actual admin check
        await message.reply("❌ This command is for admins only")
        return
    
    try:
        # Get all channels
        result = await session.execute(select(Channel))
        channels = result.scalars().all()
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="➕ Add Channel",
                callback_data="channel_add"
            )],
            [types.InlineKeyboardButton(
                text="📋 List Channels",
                callback_data="channel_list"
            )]
        ])
        
        if channels:
            keyboard.inline_keyboard.append(
                [types.InlineKeyboardButton(
                    text="🗑️ Remove Channel",
                    callback_data="channel_remove"
                )]
            )
        
        await message.reply(
            "📱 <b>Channel Management</b>\n\n"
            f"Total channels: {len(channels)}\n"
            f"Required channels: {sum(1 for c in channels if c.required)}\n\n"
            "Select an action:",
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error in channels command: {e}")
        await message.reply("❌ An error occurred")


@router.callback_query(F.data == "channel_list")
async def show_channels(
    query: CallbackQuery,
    session: AsyncSession
):
    """Show list of configured channels"""
    try:
        result = await session.execute(select(Channel))
        channels = result.scalars().all()
        
        if not channels:
            await query.answer("No channels configured")
            return
        
        text = "<b>📋 Configured Channels:</b>\n\n"
        for i, channel in enumerate(channels, 1):
            status = "✅ Required" if channel.required else "⚠️ Optional"
            text += f"{i}. {channel.title}\n"
            text += f"   ID: <code>{channel.telegram_id}</code>\n"
            text += f"   {status}\n\n"
        
        await query.message.edit_text(
            text,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error listing channels: {e}")
        await query.answer("Error occurred", show_alert=True)


@router.callback_query(F.data.startswith("force_join_"))
async def handle_force_join(
    query: CallbackQuery,
    session: AsyncSession
):
    """
    Handle force join link click
    """
    action = query.data.split("_")[2]  # join or join_complete
    
    if action == "join":
        # Send join link
        channel_id = query.data.split("_")[-1]
        
        try:
            channel = await session.get(Channel, int(channel_id))
            if not channel:
                await query.answer("Channel not found")
                return
            
            # Get invite link
            try:
                invite_link = await query.bot.create_chat_invite_link(
                    chat_id=channel.telegram_id,
                    expire_date=86400  # 24 hours
                )
                
                keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[
                    types.InlineKeyboardButton(
                        text="✅ I joined the channel",
                        callback_data=f"force_join_joined_{channel.id}"
                    )
                ]])
                
                await query.message.edit_text(
                    f"📱 Please join our channel: <b>{channel.title}</b>\n\n"
                    f"Click the button below to join, then click 'I joined'",
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
                
                try:
                    await query.answer()
                except Exception:
                    pass
                
            except Exception as e:
                logger.error(f"Error creating invite link: {e}")
                await query.answer("Failed to create invite link", show_alert=True)
        
        except Exception as e:
            logger.error(f"Error handling force join: {e}")
            await query.answer("Error occurred", show_alert=True)
    
    elif action == "joined":
        # Check if user joined
        channel_id = query.data.split("_")[-1]
        
        try:
            channel = await session.get(Channel, int(channel_id))
            
            # Check membership
            try:
                member = await query.bot.get_chat_member(
                    chat_id=channel.telegram_id,
                    user_id=query.from_user.id
                )
                
                if member.status not in ["left", "kicked"]:
                    # User is member
                    await query.answer("✅ Thanks for joining!")
                    await query.message.edit_text(
                        "✅ <b>Success!</b>\n\n"
                        "You've joined the channel and can now continue.",
                        parse_mode="HTML"
                    )
                else:
                    await query.answer(
                        "❌ You haven't joined yet. Please join first.",
                        show_alert=True
                    )
            
            except Exception as e:
                logger.error(f"Error checking membership: {e}")
                await query.answer("Error checking membership", show_alert=True)
        
        except Exception as e:
            logger.error(f"Error: {e}")
            await query.answer("Error occurred", show_alert=True)


async def check_force_join(
    user_id: int,
    session: AsyncSession,
    bot
) -> tuple[bool, list]:
    """
    Check if user has joined all required channels
    
    Returns: (all_joined: bool, missing_channels: list[Channel])
    """
    try:
        # Get all required channels
        result = await session.execute(
            select(Channel).where(Channel.required == True)
        )
        required_channels = result.scalars().all()
        
        if not required_channels:
            return True, []
        
        missing = []
        for channel in required_channels:
            try:
                member = await bot.get_chat_member(
                    chat_id=channel.telegram_id,
                    user_id=user_id
                )
                if member.status in ["left", "kicked"]:
                    missing.append(channel)
            except Exception as e:
                logger.warning(f"Error checking membership in {channel.id}: {e}")
                missing.append(channel)
        
        return len(missing) == 0, missing
    
    except Exception as e:
        logger.error(f"Error in check_force_join: {e}")
        return False, []


async def send_force_join_message(
    message: Message,
    missing_channels: list,
    session: AsyncSession
):
    """Send force-join prompt to user"""
    try:
        if not missing_channels:
            return
        
        text = "📱 <b>Join Required Channels</b>\n\n"
        text += "Please join the following channels to continue:\n\n"
        
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[])
        
        for channel in missing_channels:
            text += f"• {channel.title}\n"
            keyboard.inline_keyboard.append([
                types.InlineKeyboardButton(
                    text=f"Join {channel.title}",
                    callback_data=f"force_join_join_{channel.id}"
                )
            ])
        
        text += "\nAfter joining all channels, you can continue using the bot."
        
        await message.reply(
            text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    except Exception as e:
        logger.error(f"Error sending force-join message: {e}")


__all__ = ["router", "check_force_join", "send_force_join_message"]
