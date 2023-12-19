from chalice import Blueprint
from rules_system.controllers import RuleController
from rules_system.helpers.response import response


rules = Blueprint(__name__)

@rules.route('/rules/{_id}')
def rules_get(_id:str):
    rule_controller = RuleController()
    return response(rule_controller.get(_id))

@rules.route('/rules', methods=['POST'])
def rules_post():
    rule_controller = RuleController(rules.current_request)
    return response(rule_controller.post())

@rules.route('/rules/{_id}', methods=['PUT'])
def rules_put(_id:str):
    rule_controller = RuleController(rules.current_request)
    return response(rule_controller.put(_id))

@rules.route('/rules/{_id}', methods=['DELETE'])
def rules_delete(_id:str):
    rule_controller = RuleController()
    return response(rule_controller.delete(_id))