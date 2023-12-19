import json
from app import app
from chalice.test import Client
from tests.test_base import TestBase
from tests import db
from rules_system.models import RuleAction


class TestRuleAction(TestBase):

    def test_rule_action_table(self):
        rule_action = RuleAction(
            id=123,
            name="Name",
            action="webhook",
            data="https://google.com"
        )
        db.add(rule_action)
        db.commit()

        result = db.query(RuleAction).all()
        assert len(result) > 0
        assert result[0].name == 'Name'
        
    
    def test_post_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }

            response = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            self.assertEqual(response.json_body.get('action'), request_body.get('action'))
            self.assertEqual(response.json_body.get('data'), request_body.get('data'))
    
    
    def test_post_bad_request(self):
        with Client(app) as client:
            request_body = {
                "name": "Websocket",
                "action": "websocket",
                "data": "ws://google.com"
            }
            response = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json_body.get('error'), 
                             'Action type must be one of: webhook, email, fulfillment')
            
            
    def test_get_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }
            action_data = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            response = client.http.get(f"/rule_actions/{action_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            self.assertEqual(response.json_body.get('action'), request_body.get('action'))
            self.assertEqual(response.json_body.get('data'), request_body.get('data'))
            

    def test_get_not_found(self):
        with Client(app) as client:
            response = client.http.get(f"/rule_actions/123456")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json_body.get('error'), 
                             "Rule action with id '123456' not found.")
            
    
    def test_put_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }
            post_data = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            self.assertEqual(post_data.get('action'), request_body.get('action'))
            
            request_body['action'] = 'email'
            client.http.put(
                f"/rule_actions/{post_data.get('id')}",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            response = client.http.get(f"/rule_actions/{post_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            self.assertEqual(response.json_body.get('action'), 'email')
            
            
    def test_put_not_found(self):
        with Client(app) as client:
            request_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }
            put_data = client.http.put(
                f"/rule_actions/123456",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
                        
            self.assertEqual(put_data.status_code, 404)
            self.assertEqual(put_data.json_body.get('error'), 
                             "Rule action with id '123456' not found.")
            
            
    def test_put_bad_request(self):
        with Client(app) as client:
            request_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }
            post_data = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
                        
            request_body['action'] = 'websocket'
            put_data = client.http.put(
                f"/rule_actions/{post_data.get('id')}",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(put_data.status_code, 400)
            self.assertEqual(put_data.json_body.get('error'), 
                             'Action type must be one of: webhook, email, fulfillment')
            
    
    def test_delete_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }
            post_data = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            response = client.http.get(f"/rule_actions/{post_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            
            client.http.delete(f"/rule_actions/{post_data.get('id')}")
            
            response = client.http.get(f"/rule_actions/{post_data.get('id')}")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json_body.get('error'), 
                             f"Rule action with id '{post_data.get('id')}' not found.")
            
    
    def test_delete_not_found(self):
        with Client(app) as client:
            delete_data = client.http.delete(f"/rule_actions/123456")
            
            self.assertEqual(delete_data.status_code, 404)
            self.assertEqual(delete_data.json_body.get('error'), 
                             f"Rule action with id '123456' not found.")