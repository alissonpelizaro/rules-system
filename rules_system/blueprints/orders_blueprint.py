from chalice import Blueprint
from rules_system.controllers import OrderController
from rules_system.helpers.response import response

orders = Blueprint(__name__)

@orders.route('/orders/{_id}')
def orders_get(_id:str):
    order_controller = OrderController()
    return response(order_controller.get(_id))

@orders.route('/orders', methods=['POST'])
def orders_post():
    order_controller = OrderController(orders.current_request)
    return response(order_controller.post())

@orders.route('/orders/{_id}', methods=['PUT'])
def orders_put(_id:str):
    order_controller = OrderController(orders.current_request)
    return response(order_controller.put(_id))

@orders.route('/orders/{_id}', methods=['DELETE'])
def orders_delete(_id:str):
    order_controller = OrderController()
    return response(order_controller.delete(_id))