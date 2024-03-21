from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

from qconcursos_questoes_db.config import config

db = create_engine(config['DATABASE_URI'], pool_recycle=15)
Session = scoped_session(
    sessionmaker(autocommit=False, autoflush=False, bind=db)
)
