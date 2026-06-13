"""Channel service - force-join management"""
from sqlalchemy.ext.asyncio import AsyncSession
from database.models import Channel
from sqlalchemy import select
from utils.db_utils import scalars_first, scalars_all


class ChannelService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_active_channels(self) -> list:
        result = await self.db.execute(
            select(Channel).where(Channel.is_active == True)
        )
        return await scalars_all(result)

    async def add_channel(self, channel_id: int, channel_name: str, invite_link: str = None) -> Channel:
        channel = Channel(
            channel_id=channel_id,
            channel_name=channel_name,
            invite_link=invite_link,
            is_active=True
        )
        self.db.add(channel)
        await self.db.commit()
        await self.db.refresh(channel)
        return channel

    async def remove_channel(self, channel_id: int):
        result = await self.db.execute(
            select(Channel).where(Channel.channel_id == channel_id)
        )
        channel = await scalars_first(result)
        
        if channel:
            channel.is_active = False
            await self.db.commit()
            return True
        
        return False


__all__ = ["ChannelService"]
