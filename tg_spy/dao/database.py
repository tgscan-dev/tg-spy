from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from tg_spy.conf.env import settings

engine = create_engine(settings.postgres_connection_string(), connect_args={})

DBSession = sessionmaker(bind=engine)


# if __name__ == '__main__':
#     with DBSession() as db_session:
#         offsets = db_session.query(SypOffsets).all()
#         for offset in offsets:
#             new_username = offset.link.split("/")[-1]
#             offset.username = new_username
#             db_session.commit()
