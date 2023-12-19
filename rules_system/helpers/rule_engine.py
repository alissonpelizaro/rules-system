import pickle
import requests
from rules_system.logger import logger
from typing import List
from rules_system.types.enum_rule_action import RuleAction as EnumAction
from rules_system.config.database import Session
from rules_system.config.redis import get_redis_instance
from rules_system.models import (RuleAction, Rule)
from rules_system.exceptions import (InvalidFilterException,
                                     InvalidFilterOperationException,
                                     RuleFilterOperationMissingFieldException,
                                     MissingRuleKeyException,
                                     InvalidActionTypeException)

class RuleEngine:
    """Class for processing rules and executing associated actions."""

    __operations_list = {
        'is' :               { 'fields' : ['value'] },
        'is_not' :           { 'fields' : ['value'] },
        'is_empty' :         { 'fields' : [] },
        'is_not_empty' :     { 'fields' : [] },
        'contains' :         { 'fields' : ['value'] },
        'does_not_contain' : { 'fields' : ['value'] },
        'starts_with' :      { 'fields' : ['value'] },
        'ends_with' :        { 'fields' : ['value'] }
    }
    
    __action_list = ['webhook', 'email', 'fulfillment']
    
    @classmethod
    def process_event(cls, data:dict, entity:str, redis_instance=False) -> list:
        """Processes an event based on the specified rules.

        Args:
            data (dict): Data of the event.
            entity (str): Entity associated with the event.
            redis_instance (any): Pre initiated redis instance (optional)
            
        Returns:
            list: List of triggered rules ID.
        """
        redis = redis_instance or get_redis_instance()
        rules_ids = redis.keys(f"rule_filter#{entity}#*")
        rules = redis.mget(rules_ids)
        rules_triggered = []
        for rule_id, rule_filter in zip(rules_ids, rules):
            func = pickle.loads(rule_filter)
            filter_space={}
            exec(func, filter_space)
            
            if filter_space['exec_filter'](data, entity):
                rule_id = rule_id.decode('utf-8').split("#").pop()
                _ = cls.__exec_rule_actions(rule_id, data)
                rules_triggered.append(rule_id)
        return rules_triggered    
    
    @classmethod
    def prepare_filter(cls, filters:list) -> list:
        """Prepares and validates a list of filters for rule application.

        Args:
            filters (list): List of filters to be prepared.

        Returns:
            list: Validated list of filters.
        """
        if filters and type(filters) != list:
            raise InvalidFilterException
        return cls.__validade_rule_operations(filters)
    
    
    @classmethod
    def __validade_rule_operations(cls, filters:list) -> list:
        """Validates the operations of rule filters.

        Args:
            filters (list): List of filters to be validated.

        Returns:
            list: Validated list of filters.
        """
        _filter_list = []
        for _filter in filters:
            if _filter.get('key') == None:
                raise MissingRuleKeyException()
            if _filter.get('operation') not in cls.__operations_list: 
                raise InvalidFilterOperationException(list(cls.__operations_list))
            _filter_list.append(cls.__validade_rule_fields(_filter))
        return _filter_list
    
    
    @classmethod
    def __validade_rule_fields(cls, _filter:dict) -> dict:
        """Validates the fields of a rule filter.

        Args:
            _filter (dict): Rule filter to be validated.

        Returns:
            dict: Validated rule filter.
        """
        field_data = cls.__operations_list.get(_filter.get('operation'))
        filter_data = {
            'key': _filter.get('key'),
            'operation': _filter.get('operation')
        }
        for field in field_data.get('fields'):
            if field not in _filter:
                raise RuleFilterOperationMissingFieldException(
                    _filter.get('operation'), field)
            filter_data[field] = _filter.get(field)
        return filter_data
    
      
    @classmethod
    def validate_actions(cls, actions:List[str]) -> List[str]:
        """Validates the actions associated with a rule.

        Args:
            actions (List): List of actions to be validated.

        Returns:
            List[str]: Valid list of actions.
        """
        if type(actions) != list:
            return []
        
        ids_list = [action for action in actions if isinstance(action, str)]
        session = Session()
        rule_actions = session.query(RuleAction).filter(
            RuleAction.id.in_(ids_list)
        ).all()
        session.close()
        return [rule_action.id for rule_action in rule_actions]
    
    
    @classmethod
    def validate_action_type(cls, action_type:str) -> str:
        """Validates the type of action.

        Args:
            action_type (str): Action type to be validated.

        Returns:
            str: Validated action type.
        """
        if action_type not in cls.__action_list:
            raise InvalidActionTypeException(cls.__action_list)
        return action_type
    
    
    @classmethod
    def set_function_cache(cls, rule:Rule, redis_instance = None) -> None:
        """Caches the filter function associated with a rule.

        Args:
            rule (Rule): Rule to be cached.
            redis_instance (any): Pre initiated redis instance (optional)
        """
        redis = redis_instance or get_redis_instance()
        if rule.enabled:
            pickled_filter = cls.get_pickled_filter(rule)
            redis.set(f"rule_filter#{rule.entity}#{rule.id}", pickled_filter)
        else:
            cls.delete_function_cache(rule)
        
        
    @classmethod
    def delete_function_cache(cls, rule:Rule, redis_instance = None) -> None:
        """Removes the cached filter function associated with a rule.

        Args:
            rule (Rule): Rule to be removed from the cache.
            redis_instance (any): Pre initiated redis instance (optional)
        """
        redis = redis_instance or get_redis_instance()
        redis.delete(f"rule_filter#{rule.entity}#{rule.id}")
            
                
    @classmethod
    def get_pickled_filter(cls, rule: Rule):
        """Generates a Pickle object for the rule's filter function.

        Args:
            rule (Rule): Rule for which the filter function will be generated.

        Returns:
            Pickle: Pickle object of the filter function.
        """
        function = f"""
def exec_filter(event:any, entity:str) -> bool:
    return (
        entity == '{rule.entity}' and
        (
            {cls.generate_custom_filters_conditions(rule.filters)}
        )
    )"""
        return pickle.dumps(function)
    
    
    @classmethod
    def generate_custom_filters_conditions(cls, rule_filters: list) -> str:
        """Generates custom filter conditions in Python syntax.

        Args:
            rule_filters (list): List of custom filters.

        Returns:
            str: Filter conditions in Python syntax.
        """
        filters = ""
        for _filter in rule_filters:
            if filters != "":
                filters = f'{filters} and '
            key = _filter.get('key')

            if _filter.get('operation') == 'is':
                filters = f"{filters}event.data.get('{key}') == '{_filter.get('value')}'"
            elif _filter.get('operation') == 'is_not':
                filters = f"{filters}event.data.get('{key}') != '{_filter.get('value')}'"
            elif _filter.get('operation') == 'is_empty':
                filters = f"{filters} not event.data.get('{key}')"
            elif _filter.get('operation') == 'is_not_empty':
                filters = f"{filters}event.data.get('{key}') != ''"
            elif _filter.get('operation') == 'contains':
                filters = f"{filters}'{_filter.get('value')}' in event.data.get('{key}')"
            elif _filter.get('operation') == 'does_not_contain':
                filters = f"{filters}'{_filter.get('value')}' not in event.data.get('{key}')"
            elif _filter.get('operation') == 'starts_with':
                filters = f"{filters}event.data.get('{key}').startswith('{_filter.get('value')}')"
            elif _filter.get('operation') == 'ends_with':
                filters = f"{filters}event.data.get('{key}').endswith('{_filter.get('value')}')"

        return filters if filters != "" else "True"
    
    
    @classmethod
    def __exec_rule_actions(cls, rule_id:str, data:dict) -> None:
        """Executes the actions associated with a rule.

        Args:
            rule_id (str): ID of the rule.
            data (dict): Data of the event.
        """
        session = Session()
        rule = session.query(Rule).get(rule_id)
        actions_executed = []
        if rule and len(rule.actions) > 0:
            rule_actions = session.query(RuleAction).filter(
                RuleAction.id.in_(rule.actions)    
            ).all()
            for action in rule_actions:
                action_id = cls.__perform_action(action, data)
                if action_id:
                    actions_executed.append(action_id)
        return actions_executed
            
                
    @classmethod 
    def __perform_action(cls, rule_action:RuleAction, data:dict) -> None:
        """Executes a specific action.

        Args:
            rule_action (RuleAction): Action to be executed.
            data (dict): Data of the event.
        """
        action_map = {
            EnumAction.webhook:cls.__exec_webhook_action,
            EnumAction.email:cls.__exec_email_action,
            EnumAction.fulfillment:cls.__exec_fulfillment_action,
        }
        if rule_action.action in action_map:
            return action_map.get(rule_action.action)(rule_action, data)


    @classmethod
    def __exec_webhook_action(cls, rule_action:RuleAction, event_data:dict):
        """Executes a webhook action.

        Args:
            rule_action (RuleAction): Webhook action to be executed.
            event_data (dict): Data of the event.

        Returns:
            None
        """
        try:
            response = requests.post(
                rule_action.data,
                json=event_data.data,
                timeout=15
            )
            response.raise_for_status()
            logger.error(f"[WEBHOOK ACTION]: 'Success requested for: {rule_action.data}'")
            return rule_action.id
        except Exception as e:
            logger.error(f"[WEBHOOK ACTION EXCEPTION]: '{str(e)}'")
            
    
    @classmethod
    def __exec_email_action(cls, rule_action:RuleAction, event_data:dict):
        """Executes an email action.

        Args:
            rule_action (RuleAction): Email action to be executed.
            event_data (dict): Data of the event.
        """
        # TODO: E-mail broker service should be implemented here.
        logger.error(f"[EMAIL ACTION]: 'Email body: '{event_data.data}'")
        logger.error(f"[EMAIL ACTION]: 'Sending e-mail for '{rule_action.data}'")
        return rule_action.id
        
    
    @classmethod
    def __exec_fulfillment_action(cls, rule_action:RuleAction, event_data:dict):
        """Executes a fulfillment action.

        Args:
            rule_action (RuleAction): Fulfillment action to be executed.
            event_data (dict): Data of the event.
        """
        try:
            data = event_data.data
            # Event data can be used by the fulfillment script
            exec(rule_action.data)
            logger.error(f"[FULFILLMENT ACTION]: 'Success executed'")
            return rule_action.id
        except Exception as e:
            logger.error(f"[FULFILLMENT ACTION EXCEPTION]: '{str(e)}'")