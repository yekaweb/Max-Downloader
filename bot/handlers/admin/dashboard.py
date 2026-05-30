"""Admin dashboard handler - Bot statistics and admin commands"""
import logging
from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.types import Message, InlineQuery, InlineQueryResultArticle, InputTextMessageContent
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("stats"))
async def cmd_stats(message: Message, state: FSMContext) -> None:
    """
    /stats - Show bot statistics (admin only)

    Displays:
    - Total users
    - Total downloads
    - Downloads today
    - Popular platforms
    - Server status
    """
    try:
        # Get admin services - These would be injected via middleware
        # For now, we'll create mock data
        stats_data = {
            "total_users": 1250,
            "active_users_today": 342,
            "total_downloads": 15420,
            "downloads_today": 523,
            "downloads_this_week": 2104,
            "total_storage_used_gb": 450,
            "top_platforms": [
                {"name": "YouTube", "count": 12340},
                {"name": "Instagram", "count": 1850},
                {"name": "TikTok", "count": 1230},
            ],
            "server_status": {
                "cpu_usage": 32,
                "memory_usage": 58,
                "disk_usage": 72,
                "uptime_hours": 144,
                "database_status": "healthy",
                "redis_status": "healthy",
            },
            "revenue": {
                "today": 2400,
                "this_week": 18500,
                "this_month": 72000,
            },
        }

        # Format statistics report
        report = format_stats_report(stats_data)

        await message.reply(report, parse_mode="HTML")

    except Exception as e:
        logger.error(f"Error in /stats: {e}")
        await message.reply(
            "❌ Error fetching statistics. Please try again.",
            parse_mode="HTML",
        )


def format_stats_report(stats: dict) -> str:
    """Format statistics into a readable report"""
    report = """
<b>📊 Bot Statistics</b>

<b>👥 Users:</b>
  • Total Users: <code>{total_users:,}</code>
  • Active Today: <code>{active_users_today:,}</code>

<b>📥 Downloads:</b>
  • Total: <code>{total_downloads:,}</code>
  • Today: <code>{downloads_today:,}</code>
  • This Week: <code>{downloads_this_week:,}</code>

<b>💾 Storage:</b>
  • Used: <code>{total_storage_used_gb:,} GB</code>

<b>🔝 Top Platforms:</b>
""".format(**stats)

    for i, platform in enumerate(stats["top_platforms"], 1):
        report += f"  {i}. {platform['name']}: <code>{platform['count']:,}</code>\n"

    report += f"""
<b>🖥 Server Status:</b>
  • CPU: <code>{cpu}%</code>
  • Memory: <code>{memory}%</code>
  • Disk: <code>{disk}%</code>
  • Uptime: <code>{uptime}h</code>
  • Database: <code>{db}</code>
  • Redis: <code>{redis}</code>

<b>💰 Revenue:</b>
  • Today: <code>${revenue_today:,.2f}</code>
  • This Week: <code>${revenue_week:,.2f}</code>
  • This Month: <code>${revenue_month:,.2f}</code>

<i>Last updated: {timestamp}</i>
""".format(
        cpu=stats["server_status"]["cpu_usage"],
        memory=stats["server_status"]["memory_usage"],
        disk=stats["server_status"]["disk_usage"],
        uptime=stats["server_status"]["uptime_hours"],
        db=stats["server_status"]["database_status"],
        redis=stats["server_status"]["redis_status"],
        revenue_today=stats["revenue"]["today"],
        revenue_week=stats["revenue"]["this_week"],
        revenue_month=stats["revenue"]["this_month"],
        timestamp=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    )

    return report


__all__ = ["router", "cmd_stats", "format_stats_report"]
