from chalice import Blueprint
from rules_system.controllers import RuleActionController
from rules_system.helpers.response import response


rule_actions = Blueprint(__name__)

@rule_actions.route('/rule_actions/{_id}')
def rules_get(_id:str):
    action_controller = RuleActionController()
    return response(action_controller.get(_id))

@rule_actions.route('/rule_actions', methods=['POST'])
def rules_post():
    action_controller = RuleActionController(rule_actions.current_request)
    return response(action_controller.post())

@rule_actions.route('/rule_actions/{_id}', methods=['PUT'])
def rules_put(_id:str):
    action_controller = RuleActionController(rule_actions.current_request)
    return response(action_controller.put(_id))

@rule_actions.route('/rule_actions/{_id}', methods=['DELETE'])
def rules_delete(_id:str):
    action_controller = RuleActionController()
    return response(action_controller.delete(_id))