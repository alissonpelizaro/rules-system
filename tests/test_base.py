from unittest import TestCase
from tests import db
from rules_system.models import Order, Payment, Rule, RuleAction


class TestBase(TestCase):
    
    def setUp(self):
        db.query(Order).delete()
        db.query(Payment).delete()
        db.query(Rule).delete()
        db.query(RuleAction).delete()
        db.commit()


    def tearDown(self):
        db.query(Order).delete()
        db.query(Payment).delete()
        db.query(Rule).delete()
        db.query(RuleAction).delete()
        db.commit()