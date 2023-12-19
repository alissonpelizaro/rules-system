from enum import Enum

class RuleAction(Enum):
    webhook     = 'webhook'
    email       = 'email'
    fulfillment = 'fulfillment'
