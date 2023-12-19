import sys
sys.modules['pytest'] = True

import os
os.environ['DATABASE_URL'] = "sqlite:///:memory:"

from app import app
from rules_system.config.database import Session, engine
from rules_system import models

db = Session()
models.Base.metadata.create_all(engine)