from enum import Enum
from datetime import datetime
from sqlalchemy import String, DateTime
from sqlalchemy.orm import MappedAsDataclass, DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import declared_attr
from rules_system.config import Session


class BaseModel(MappedAsDataclass, DeclarativeBase):
    """define a series of common elements that may be applied to mapped
    classes using this class as a base class."""

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    __mapper_args__ = {"eager_defaults": True}

    id: Mapped[str] = mapped_column(
        String, primary_key=True, nullable=False, doc='Id')
    created_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, init=False, default_factory=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, init=False, default_factory=datetime.now, onupdate=datetime.now)


    def jsonable(self) -> dict:
        """Returns model data serializable and ready to be used as JSON.

        Returns:
            dict: A dictionary containing serialized model data.
        """
        data = {}
        for c in self.__table__.columns:
            data[c.name] = getattr(self, c.name)
            if isinstance(data[c.name], datetime):
                data[c.name] = data[c.name].strftime('%Y-%m-%dT%H:%M:%SZ')
            elif isinstance(data[c.name], Enum):
                data[c.name] = data[c.name].value
        return data

    
    def save(self, commit=True) -> None:
        """Saves the model to the database.

        Args:
            commit (bool, optional): If True, commits the changes to the
                                     database; otherwise, only adds the object.
                                     Defaults to True.

        Raises:
            Exception: Any exception raised during the database commit.
                       Rolls back the transaction if an exception occurs.
        """
        with Session() as session:
            session.add(self)
            if commit:
                try:
                    session.commit()
                except Exception as e:
                    session.rollback()
                    raise e

