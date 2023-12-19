import uuid
from .base_controller import BaseController
from rules_system.config.database import Session
from rules_system.models import Payment
from rules_system.helpers.rule_engine import RuleEngine


class PaymentController(BaseController):
    """Controller class for managing payments.
    
    Methods:
        - get(_id: str): Retrieves the details of a payment by its ID.
        - post(): Creates a new payment with the provided data.
        - put(_id: str): Updates an existing payment with the provided data.
        - delete(_id: str): Deletes an payment by its ID.
    """
    
    def get(self, _id:str):
        """Retrieves the details of an payment by its ID.

        Args:
            _id (str): Identifier for the payment.

        Returns:
            dict or tuple: JSON-serializable payment data or an error message with
                          a corresponding HTTP status code.
        """
        session = Session()
        payment = session.query(Payment).get(_id)
        session.close()
        if payment:
            return payment.jsonable().get('data')
        return f"Payment with id '{_id}' not found.", 404
    
    
    def post(self):
        """Creates a new payment with the provided data.

        Returns:
            dict or tuple: JSON-serializable payment data or an error message with
                          a corresponding HTTP status code.
        """
        payment_id = str(uuid.uuid4())
        payment_data = self.request.json_body
        try:
            payment = Payment(
                id=payment_id,
                data=payment_data
            )
            payment.save()
            RuleEngine.process_event(payment, 'payment')
            return payment.jsonable(), 201
        except Exception as e:
            return e.args[0], 400
    
    
    def put(self, _id:str):
        """Updates an existing payment with the provided data.

        Args:
            _id (str): Identifier for the payment.

        Returns:
            dict or tuple: JSON-serializable updated payment data or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        payment_data = self.request.json_body
        payment = session.query(Payment).get(_id)
        session.close()
        if payment:
            try:
                payment.data=payment_data
                payment.save()
                RuleEngine.process_event(payment, 'payment')
                return payment.jsonable()
            except Exception as e:
                return e.args[0], 400
        return f"Payment with id '{_id}' not found.", 404

    
    def delete(self, _id:str):
        """Deletes an payment by its ID.

        Args:
            _id (str): Identifier for the payment.

        Returns:
            dict or tuple: JSON-serializable success message or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        payment = session.query(Payment).get(_id)
        if payment:
            session.delete(payment)
            session.commit()
            session.close()
            return {'message': 'Deleted succesfully'}
        session.close()
        return f"Payment with id '{_id}' not found.", 404