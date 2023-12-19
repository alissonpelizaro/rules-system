from chalice import Blueprint
from rules_system.controllers import PaymentController
from rules_system.helpers.response import response

payments = Blueprint(__name__)

@payments.route('/payments/{_id}')
def payments_get(_id:str):
    payment_controller = PaymentController()
    return response(payment_controller.get(_id))

@payments.route('/payments', methods=['POST'])
def payments_post():
    payment_controller = PaymentController(payments.current_request)
    return response(payment_controller.post())

@payments.route('/payments/{_id}', methods=['PUT'])
def payments_put(_id:str):
    payment_controller = PaymentController(payments.current_request)
    return response(payment_controller.put(_id))

@payments.route('/payments/{_id}', methods=['DELETE'])
def payments_delete(_id:str):
    payment_controller = PaymentController()
    return response(payment_controller.delete(_id))