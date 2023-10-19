import asyncio

from tg_spy.service.msg_spy import MsgSyp

if __name__ == "__main__":
    syp = MsgSyp()
    asyncio.run(syp.run())
