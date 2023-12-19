from . import BaseModel
from sqlalchemy import String, Enum
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from rules_system.types import RuleAction


class RuleAction(BaseModel):
    
    __tablename__ = 'rule_action'

    name: Mapped[str] = mapped_column(String, 
                                      init=True, 
                                      default='', 
                                      nullable=False)
    action: Mapped[str] = mapped_column(Enum(RuleAction), 
                                      init=True,
                                      default=RuleAction.webhook,
                                      nullable=False)
    data: Mapped[dict] = mapped_column(String, 
                                       default=None, 
                                       nullable=True)