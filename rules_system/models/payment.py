from . import BaseModel
from sqlalchemy import String, Boolean
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from rules_system.types import JSONB, ARRAY


class Payment(BaseModel):
    
    data: Mapped[dict] = mapped_column(JSONB(), 
                                          default=None, 
                                          nullable=True)
