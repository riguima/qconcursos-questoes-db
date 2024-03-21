from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from qconcursos_questoes_db.database import db


class Base(DeclarativeBase):
    pass


class Question(Base):
    __tablename__ = 'questoes'
    id: Mapped[int] = mapped_column(primary_key=True)
    numero: Mapped[str] = mapped_column(String(20))
    questao: Mapped[str] = mapped_column(String(500))
    alternativas: Mapped[str] = mapped_column(String(500))
    resposta: Mapped[str] = mapped_column(String(200))
    materia: Mapped[str] = mapped_column(String(50))
    ano: Mapped[int]
    banca: Mapped[str] = mapped_column(String(50))
    orgao: Mapped[str] = mapped_column(String(100))
    prova: Mapped[str] = mapped_column(String(100))
    imagens: Mapped[str] = mapped_column(String(500))


Base.metadata.create_all(db)
