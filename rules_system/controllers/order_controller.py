import uuid
from .base_controller import BaseController
from rules_system.config.database import Session
from rules_system.models import Order
from rules_system.helpers.rule_engine import RuleEngine


class OrderController(BaseController):
    """Controller class for managing orders.
    
    Methods:
        - get(_id: str): Retrieves the details of an order by its ID.
        - post(): Creates a new order with the provided data.
        - put(_id: str): Updates an existing order with the provided data.
        - delete(_id: str): Deletes an order by its ID.
    """
    
    def get(self, _id:str):
        """Retrieves the details of an order by its ID.

        Args:
            _id (str): Identifier for the order.

        Returns:
            dict or tuple: JSON-serializable order data or an error message with
                          a corresponding HTTP status code.
        """
        session = Session()
        order = session.query(Order).get(_id)
        session.close()
        if order:
            return order.jsonable().get('data')
        return f"Order with id '{_id}' not found.", 404
    
    
    def post(self):
        """Creates a new order with the provided data.

        Returns:
            dict or tuple: JSON-serializable order data or an error message with
                          a corresponding HTTP status code.
        """
        order_id = str(uuid.uuid4())
        order_data = self.request.json_body
        try:
            order = Order(
                id=order_id,
                data=order_data
            )
            order.save()
            RuleEngine.process_event(order, 'order')
            return order.jsonable(), 201
        except Exception as e:
            return e.args[0], 400
    
    
    def put(self, _id:str):
        """Updates an existing order with the provided data.

        Args:
            _id (str): Identifier for the order.

        Returns:
            dict or tuple: JSON-serializable updated order data or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        order_data = self.request.json_body
        order = session.query(Order).get(_id)
        session.close()
        if order:
            try:
                order.data=order_data
                order.save()
                RuleEngine.process_event(order, 'order')
                return order.jsonable()
            except Exception as e:
                return e.args[0], 400
        return f"Order with id '{_id}' not found.", 404

    
    def delete(self, _id:str):
        """Deletes an order by its ID.

        Args:
            _id (str): Identifier for the order.

        Returns:
            dict or tuple: JSON-serializable success message or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        order = session.query(Order).get(_id)
        if order:
            session.delete(order)
            session.commit()
            session.close()
            return {'message': 'Deleted succesfully'}
        session.close()
        return f"Order with id '{_id}' not found.", 404