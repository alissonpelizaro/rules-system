import uuid
import pickle
from unittest.mock import patch, PropertyMock
from tests.test_base import TestBase
from rules_system.config.redis import get_redis_instance
from rules_system.models import Order, Payment, Rule, RuleAction
from rules_system.helpers.rule_engine import RuleEngine
from rules_system.exceptions import (InvalidFilterException,
                                     MissingRuleKeyException,
                                     InvalidFilterOperationException,
                                     RuleFilterOperationMissingFieldException,
                                     InvalidActionTypeException)

class TestRuleEngine(TestBase):
        
    def test_process_event_empty(self):
        rule_engine = RuleEngine()
        rules = rule_engine.process_event({}, 'payment', )
        self.assertEqual(rules, [])
    
        
    def test_process_event_filter_order_matched(self):
        redis = get_redis_instance()
        rule_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="py@test.com", 
                                 action='email')
        rule_action.save()
        
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[rule_action.id])
        rule.save()
        
        order = Order(id=str(uuid.uuid4()), data={"Py": "Test"})
        order.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        rules = rule_engine.process_event(order, 'order', redis)
        self.assertEqual(rules, [rule.id])


    def test_process_event_filter_payment_matched(self):
        redis = get_redis_instance()
        rule_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="py@test.com", 
                                 action='email')
        rule_action.save()
        
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="payment",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[rule_action.id])
        rule.save()
        
        payment = Payment(id=str(uuid.uuid4()), data={"Py": "Test"})
        payment.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        rules = rule_engine.process_event(payment, 'payment', redis)
        self.assertEqual(rules, [rule.id])
        
        
    def test_process_event_filter_order_matched(self):
        redis = get_redis_instance()
        rule_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="py@test.com", 
                                 action='email')
        rule_action.save()
        
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[rule_action.id])
        rule.save()
        
        order = Order(id=str(uuid.uuid4()), data={"Py": "Test"})
        order.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        rules = rule_engine.process_event(order, 'order', redis)
        self.assertEqual(rules, [rule.id])
        
    
    def test_process_event_filter_unmatched(self):
        redis = get_redis_instance()
        rule_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="py@test.com", 
                                 action='email')
        rule_action.save()
        
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[rule_action.id])
        rule.save()
        
        order = Order(id=str(uuid.uuid4()), data={"Py": "Unitary"})
        order.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        rules = rule_engine.process_event(order, 'order', redis)
        self.assertEqual(rules, [])
        
    
    def test_prepare_filter_invalid(self):
        rule_engine = RuleEngine()
        try:
            rule_engine.prepare_filter('invalid_format')
            self.assertTrue(False)
        except InvalidFilterException:
            self.assertTrue(True)
        
    
    def test_prepare_filter_success(self):
        rule_engine = RuleEngine()
        _filter = rule_engine.prepare_filter([{
            "key" : "Py",
            "operation" : "is_not",
            "value" : "Test",
            "unecessary_data" : True
        }])
        
        self.assertEqual(_filter, [{
            "key" : "Py",
            "operation" : "is_not",
            "value" : "Test"
        }])


    def test_prepare_filter_missing_rule_key(self):
        rule_engine = RuleEngine()
        try:
            rule_engine.prepare_filter([{
                "key_wrong" : "Py",
                "operation" : "is_not",
                "value" : "Test",
            }])
            self.assertTrue(False)
        except MissingRuleKeyException:
            self.assertTrue(True)
            
    
    def test_prepare_filter_missing_rule_operation(self):
        rule_engine = RuleEngine()
        try:
            rule_engine.prepare_filter([{
                "key" : "Py",
                "operation_wrong" : "is_not",
                "value" : "Test",
            }])
            self.assertTrue(False)
        except InvalidFilterOperationException:
            self.assertTrue(True)
            
            
    def test_prepare_filter_missing_rule_value(self):
        rule_engine = RuleEngine()
        try:
            rule_engine.prepare_filter([{
                "key" : "Py",
                "operation" : "is_not",
                "value_wrong" : "Test",
            }])
            self.assertTrue(False)
        except RuleFilterOperationMissingFieldException:
            self.assertTrue(True)
            
            
    def test_prepare_multiple_filter_success(self):
        rule_engine = RuleEngine()
        _filter = rule_engine.prepare_filter([
            {"key": "Py", "operation": "is_not", "value": "Test", "Py": "Test"},
            {"key": "Test", "operation": "is", "value": "Py"},
            {"key": "unit", "operation": "is_empty"},
        ])
        
        self.assertEqual(_filter, [
            {"key": "Py", "operation": "is_not", "value": "Test"},
            {"key": "Test", "operation": "is", "value": "Py"},
            {"key": "unit", "operation": "is_empty"},
        ])
        
    
    def test_validate_actions_empty(self):
        rule_engine = RuleEngine()
        actions = rule_engine.validate_actions('')
        self.assertEqual(actions, [])
        
    
    def test_validate_actions_success(self):
        rule_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="py@test.com", 
                                 action='email')
        rule_action.save()
        
        rule_engine = RuleEngine()
        actions = rule_engine.validate_actions([rule_action.id, 'invalid_id'])
        self.assertEqual(actions, [rule_action.id])
    
    
    def test_validate_action_type_wrong(self):
        rule_engine = RuleEngine()
        try:
            rule_engine.validate_action_type('websocket')
            self.assertTrue(False)
        except InvalidActionTypeException:
            self.assertTrue(True)


    def test_validate_action_type_success(self):
        rule_engine = RuleEngine()
        self.assertEqual(rule_engine.validate_action_type('webhook'), 'webhook')
        self.assertEqual(rule_engine.validate_action_type('email'), 'email')
        self.assertEqual(rule_engine.validate_action_type('fulfillment'), 
                                                          'fulfillment')
        
    
    def test_set_function_cache_success(self):
        redis = get_redis_instance()

        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        self.assertIsNotNone(redis.get(f"rule_filter#{rule.entity}#{rule.id}"))
        
    
    def test_set_function_cache_disabled_success(self):
        redis = get_redis_instance()

        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        self.assertIsNone(redis.get(f"rule_filter#{rule.entity}#{rule.id}"))
        
    
    def test_delete_function_cache_success(self):
        redis = get_redis_instance()

        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        self.assertIsNotNone(redis.get(f"rule_filter#{rule.entity}#{rule.id}"))
        
        rule_engine.delete_function_cache(rule, redis)
        self.assertIsNone(redis.get(f"rule_filter#{rule.entity}#{rule.id}"))
    
        
    def test_get_pickled_function_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        order = Order(id=str(uuid.uuid4()), data={})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filtered_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"Test"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filter_unmatched_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"is_not","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"Test"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), False)
        
        
    def test_get_pickled_function_multiple_filter_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [
                        {"key":"Py","operation":"is","value":"Test"},
                        {"key":"Test","operation":"is_not","value":"Unity"}
                    ],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"Test", "Test": "Py"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
    
    
    def test_get_pickled_function_multiple_filter_unmatched_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [
                        {"key":"Py","operation":"is","value":"Test"},
                        {"key":"Test","operation":"is_not","value":"Unity"}
                    ],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"Test", "Test": "Unity"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), False)
    
    
    def test_get_pickled_function_filtered_is_empty_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"is_empty"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":""})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filtered_is_not_empty_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"is_not_empty"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"Content"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filtered_contains_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"contains","value":"test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"I'm a test, dude!"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filtered_does_not_contain_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"does_not_contain","value":"test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"I'm a robot, dude!"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filtered_starts_with_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"starts_with","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"Test is a good idea!"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_get_pickled_function_filtered_ends_with_success(self):
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=False, 
                    filters= [{"key":"Py","operation":"ends_with","value":"Test"}],
                    actions=[])
        rule.save()
        
        rule_engine = RuleEngine()
        func = pickle.loads(rule_engine.get_pickled_filter(rule))
        filter_space={}
        exec(func, filter_space)
        
        order = Order(id=str(uuid.uuid4()), data={"Py":"I like being a Test"})
        self.assertIs(filter_space['exec_filter'](order, 'order'), True)
        
    
    def test_exec_multiple_rule_action(self):
        """ This unitary test perforM tests on multiple functions:
            - __perform_action()
            - __exec_rule_actions()
            - __exec_webhook_action()
            - __exec_email_action()
            - __exec_fulfillment_action()
        """
        redis = get_redis_instance()
        email_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="py@test.com", 
                                 action='email')
        email_action.save()
        webhook_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data="https://test.com", 
                                 action='webhook')
        webhook_action.save()
        fulfillment_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data='print("I am a test!")', 
                                 action='fulfillment')
        fulfillment_action.save()
        
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[email_action.id, 
                             webhook_action.id, 
                             fulfillment_action.id])
        rule.save()
        
        order = Order(id=str(uuid.uuid4()), data={"Py": "Test"})
        order.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
        with patch.object(RuleEngine, 
                          '_RuleEngine__exec_webhook_action', 
                          new_callable=PropertyMock) as webhook_mock:
            webhook_mock.return_value = lambda *_: webhook_action.id
            
            rules = rule_engine.process_event(order, 'order', redis)
            self.assertEqual(rules, [rule.id])
            
            
    def test_exec_invalid_fulfilllment_action(self):
        redis = get_redis_instance()
        fulfillment_action = RuleAction(id=str(uuid.uuid4()), 
                                 name="Rule Action name",
                                 data='I am a wrong script (;)', 
                                 action='fulfillment')
        fulfillment_action.save()
        
        rule = Rule(id=str(uuid.uuid4()),
                    name="Rule name", 
                    entity="order",
                    enabled=True, 
                    filters= [{"key":"Py","operation":"is","value":"Test"}],
                    actions=[fulfillment_action.id])
        rule.save()
        
        order = Order(id=str(uuid.uuid4()), data={"Py": "Test"})
        order.save()
        
        rule_engine = RuleEngine()
        rule_engine.set_function_cache(rule, redis)
            
        rules = rule_engine.process_event(order, 'order', redis)
        self.assertEqual(rules, [rule.id])