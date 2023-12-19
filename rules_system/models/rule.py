from . import BaseModel
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from rules_system.types import JSONB, ARRAY


class Rule(BaseModel):

    name: Mapped[str] = mapped_column(String, 
                                      init=True, 
                                      default='', 
                                      nullable=False)
    entity: Mapped[str] = mapped_column(String, 
                                        init=True, 
                                        default='', 
                                        nullable=False)
    filters: Mapped[dict] = mapped_column(JSONB(), 
                                          default=None, 
                                          nullable=True)
    actions: Mapped[dict] = mapped_column(ARRAY(), 
                                          default=None, 
                                          nullable=True)
    enabled: Mapped[bool] = mapped_column(Boolean, 
                                          init=True,
                                          default=True)