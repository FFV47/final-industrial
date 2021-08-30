from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


def init_db(db_path):
    import models

    engine = create_engine(
        f"sqlite:///{db_path}", connect_args={"check_same_thread": False}
    )
    Session = sessionmaker(bind=engine)

    models.Base.metadata.create_all(engine)

    return Session
