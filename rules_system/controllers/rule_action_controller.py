import uuid
from .base_controller import BaseController
from rules_system.config.database import Session
from rules_system.models import RuleAction
from rules_system.exceptions import InvalidActionTypeException
from rules_system.helpers.rule_engine import RuleEngine


class RuleActionController(BaseController):
    """Controller class for managing rule actions.
    
    Methods:
        - get(_id: str): Retrieves the details of an action by its ID.
        - post(): Creates a new action with the provided data.
        - put(_id: str): Updates an existing action with the provided data.
        - delete(_id: str): Deletes an action by its ID.
    """
    
    def get(self, _id:str):
        """Retrieves the details of an action by its ID.

        Args:
            _id (str): Identifier for the action.

        Returns:
            dict or tuple: JSON-serializable action data or an error message with
                          a corresponding HTTP status code.
        """
        session = Session()
        rule_action = session.query(RuleAction).get(_id)
        session.close()
        if rule_action:
            return rule_action.jsonable()
        return f"Rule action with id '{_id}' not found.", 404
    
    
    def post(self):
        """Creates a new action with the provided data.

        Returns:
            dict or tuple: JSON-serializable action data or an error message with
                          a corresponding HTTP status code.
        """
        rule_action_id = str(uuid.uuid4())
        rule_action_data = self.request.json_body
        try:
            rule_action = RuleAction(
                id=rule_action_id,
                name=rule_action_data.get('name'),
                data=rule_action_data.get('data'),
                action=RuleEngine.validate_action_type(
                    rule_action_data.get('action')
                )
            )
            rule_action.save()
            return rule_action.jsonable(), 201
        except InvalidActionTypeException as e:
            return e.args[0], 400
    
    
    def put(self, _id:str):
        """Updates an existing action with the provided data.

        Args:
            _id (str): Identifier for the action.

        Returns:
            dict or tuple: JSON-serializable updated action data or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        rule_action_data = self.request.json_body
        rule_action = session.query(RuleAction).get(_id)
        session.close()
        if rule_action:
            try:
                rule_action.name = rule_action_data.get('name')
                rule_action.data = rule_action_data.get('data')
                rule_action.action = RuleEngine.validate_action_type(
                    rule_action_data.get('action')
                )
                rule_action.save(session)
                return rule_action.jsonable()
            except InvalidActionTypeException as e:
                return e.args[0], 400
        return f"Rule action with id '{_id}' not found.", 404

    
    def delete(self, _id:str):
        """Deletes an action by its ID.

        Args:
            _id (str): Identifier for the action.

        Returns:
            dict or tuple: JSON-serializable success message or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        rule_action = session.query(RuleAction).get(_id)
        if rule_action:
            session.delete(rule_action)
            session.commit()
            session.close()
            return {'message': 'Deleted succesfully'}
        session.close()
        return f"Rule action with id '{_id}' not found.", 404