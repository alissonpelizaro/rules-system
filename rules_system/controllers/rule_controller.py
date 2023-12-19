import uuid
from .base_controller import BaseController
from rules_system.config.database import Session
from rules_system.models import Rule
from rules_system.exceptions import InvalidFilterException
from rules_system.helpers.rule_engine import RuleEngine


class RuleController(BaseController):
    """Controller class for managing rules.
    
    Methods:
        - get(_id: str): Retrieves the details of a rule by its ID.
        - post(): Creates a new rule with the provided data.
        - put(_id: str): Updates an existing rule with the provided data.
        - delete(_id: str): Deletes an rule by its ID.
    """
    
    def get(self, _id:str):
        """Retrieves the details of an rule by its ID.

        Args:
            _id (str): Identifier for the rule.

        Returns:
            dict or tuple: JSON-serializable rule data or an error message with
                          a corresponding HTTP status code.
        """
        session = Session()
        rule = session.query(Rule).get(_id)
        session.close()
        if rule:
            return rule.jsonable()
        return f"Rule with id '{_id}' not found.", 404
    
    
    def post(self):
        """Creates a new rule with the provided data.

        Returns:
            dict or tuple: JSON-serializable rule data or an error message with
                          a corresponding HTTP status code.
        """
        rule_id = str(uuid.uuid4())
        rule_data = self.request.json_body
        try:
            filters = RuleEngine.prepare_filter(rule_data.get('filters'))
            rule = Rule(
                id=rule_id,
                name=rule_data.get('name'),
                entity=rule_data.get('entity'),
                enabled=rule_data.get('enabled', True),
                filters=filters,
                actions=RuleEngine.validate_actions(rule_data.get('actions'))
            )
            rule.save()
            RuleEngine.set_function_cache(rule)
            return rule.jsonable(), 201
        except InvalidFilterException as e:
            return e.args[0], 400
    
    
    def put(self, _id:str):
        """Updates an existing rule with the provided data.

        Args:
            _id (str): Identifier for the rule.

        Returns:
            dict or tuple: JSON-serializable updated rule data or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        rule_data = self.request.json_body
        rule = session.query(Rule).get(_id)
        session.close()
        if rule:
            try:
                filters = RuleEngine.prepare_filter(rule_data.get('filters'))
                RuleEngine.delete_function_cache(rule)
                rule.name=rule_data.get('name')
                rule.entity=rule_data.get('entity')
                rule.enabled=rule_data.get('enabled')
                rule.filters=filters
                rule.save()
                RuleEngine.set_function_cache(rule)
                return rule.jsonable()
            except InvalidFilterException as e:
                return e.args[0], 400
        return f"Rule with id '{_id}' not found.", 404

    
    def delete(self, _id:str):
        """Deletes an rule by its ID.

        Args:
            _id (str): Identifier for the rule.

        Returns:
            dict or tuple: JSON-serializable success message or an error message
                          with a corresponding HTTP status code.
        """
        session = Session()
        rule = session.query(Rule).get(_id)
        if rule:
            session.delete(rule)
            session.commit()
            session.close()
            RuleEngine.delete_function_cache(rule)
            return {'message': 'Deleted succesfully'}
        session.close()
        return f"Rule with id '{_id}' not found.", 404