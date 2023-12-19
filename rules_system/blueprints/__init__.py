from chalice import Chalice
from .orders_blueprint import orders
from .payments_blueprint import payments
from .rules_blueprint import rules
from .rule_actions_blueprint import rule_actions

BP_LIST = [orders, payments, rules, rule_actions]

def register_blueprints(app: Chalice) -> None:
    """
    Registers a list of blueprints with the given Chalice app.

    Parameters:
    - app (Chalice): The Chalice app instance to which the blueprints will be 
        registered.
    """
    for blueprint in BP_LIST:
        app.register_blueprint(blueprint)
