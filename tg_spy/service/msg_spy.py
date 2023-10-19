import asyncio

from loguru import logger
from telethon import TelegramClient

from tg_spy.conf.env import settings
from tg_spy.dao.database import DBSession
from tg_spy.dao.models import Message, SypOffsets

api_id = 1024
api_hash = "b18441a1ff607e10a989891a5462e627"


def parse_db_msgs(tg_msgs: list, offset) -> list[Message]:
    res = []
    for msg in tg_msgs:
        file_names = []
        if msg.document is not None:
            for attr in msg.document.attributes:
                if hasattr(attr, "file_name"):
                    file_name = attr.file_name
                    file_names.append(file_name)

        if msg.text is None or msg.text.strip() == "":
            continue
        res.append(
            Message(
                offset=msg.id,
                username=offset.username,
                sender_id=msg.sender.id,
                content="\n".join(file_names) + "\n" + msg.text,
                send_time=msg.date,
            )
        )
    return res


class MsgSyp:
    def __init__(self) -> None:
        self.tg_client = TelegramClient(settings.SESSION_FILE, api_id, api_hash)
        self.db_session = DBSession()

    async def do_grab_tg_msgs(self, username: str, offset_id: int = 0):
        messages = []
        async for msg in self.tg_client.iter_messages(
            username, reverse=True, limit=1000, offset_id=offset_id
        ):
            messages.append(msg)
        return messages

    async def run(self):
        await self.tg_client.start("9")
        logger.info("tg_client started")
        offsets = (
            self.db_session.query(SypOffsets)
            .filter(SypOffsets.crawl_link == False)
            .all()
        )
        for offset in offsets:
            await asyncio.sleep(10)
            tg_msgs = await self.grab_tg_msgs(offset)
            if len(tg_msgs) > 0:
                date = tg_msgs[-1].date
                logger.info(f"Last message date: {date}")
            if tg_msgs:
                db_msgs = parse_db_msgs(tg_msgs, offset)
                await self.save2db(db_msgs)
                offset.last_offset = tg_msgs[-1].id
                self.db_session.commit()

    async def grab_tg_msgs(self, offset):
        username = offset.username
        offset_id = offset.last_offset
        logger.info(
            f"Start fetch tg_msgs from username {username},\
room name {offset.room_name} with offset {offset_id}"
        )
        tg_msgs = await self.do_grab_tg_msgs(username, offset_id)
        logger.info(f"End fetch tg_msgs, found {len(tg_msgs)} tg_msgs")
        return tg_msgs

    async def save2db(self, db_msgs):
        for db_msg in db_msgs:
            try:
                self.db_session.add(db_msg)
                self.db_session.commit()
            except Exception as e:
                logger.error(e)
