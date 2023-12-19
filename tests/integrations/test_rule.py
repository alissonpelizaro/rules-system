import json
from app import app
from chalice.test import Client
from tests.test_base import TestBase
from tests import db
from rules_system.models import Rule


class TestRule(TestBase):

    def test_rule_table(self):
        rule = Rule(
            id=123,
            name="Name",
            entity="Pedidos",
            enabled=True,
            filters={"test":"1"}
        )
        db.add(rule)
        db.commit()

        result = db.query(Rule).all()
        assert len(result) > 0
        assert result[0].name == 'Name'
        
    
    def test_post_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": []
            }
            response = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            self.assertEqual(response.json_body.get('entity'), request_body.get('entity'))
            self.assertEqual(response.json_body.get('enabled'), request_body.get('enabled'))
            self.assertEqual(response.json_body.get('filters'), request_body.get('filters'))
            
            
    def test_post_invalid_action_id(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": [],
                "actions": ["1q2w3e4r", "4r3e2w1q"]
            }
            response = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json_body.get('actions'), [])
            
    
    def test_post_valid_action_id(self):
        with Client(app) as client:
            
            action_body = {
                "name": "Webhook",
                "action": "webhook",
                "data": "https://google.com"
            }

            action_post = client.http.post(
                '/rule_actions',
                headers={'Content-Type':'application/json'},
                body=json.dumps(action_body)
            ).json_body
            
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": [],
                "actions": ["1q2w3e4r", action_post.get('id')]
            }
            response = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json_body.get('actions'), [action_post.get('id')])
    
    
    def test_post_bad_request(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": 'invalid_filter'
            }
            response = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 400)
            self.assertEqual(response.json_body.get('error'), 
                             'Rule filter must be List type')
            
            
    def test_get_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": []
            }
            rule_data = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            response = client.http.get(f"/rules/{rule_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            self.assertEqual(response.json_body.get('entity'), request_body.get('entity'))
            self.assertEqual(response.json_body.get('enabled'), request_body.get('enabled'))
            self.assertEqual(response.json_body.get('filters'), request_body.get('filters'))
            

    def test_get_not_found(self):
        with Client(app) as client:
            response = client.http.get(f"/rules/123456")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json_body.get('error'), 
                             "Rule with id '123456' not found.")
            
    
    def test_put_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": []
            }
            post_data = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            self.assertEqual(post_data.get('entity'), request_body.get('entity'))
            
            request_body['entity'] = 'payment'
            client.http.put(
                f"/rules/{post_data.get('id')}",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            response = client.http.get(f"/rules/{post_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            self.assertEqual(response.json_body.get('entity'), 'payment')
            
            
    def test_put_not_found(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": []
            }
            put_data = client.http.put(
                f"/rules/123456",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
                        
            self.assertEqual(put_data.status_code, 404)
            self.assertEqual(put_data.json_body.get('error'), 
                             "Rule with id '123456' not found.")
            
            
    def test_put_bad_request(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": []
            }
            post_data = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
                        
            request_body['filters'] = 'invalid filter'
            put_data = client.http.put(
                f"/rules/{post_data.get('id')}",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(put_data.status_code, 400)
            self.assertEqual(put_data.json_body.get('error'), 
                             "Rule filter must be List type")
            
            
    def test_delete_success(self):
        with Client(app) as client:
            request_body = {
                "name": "Rule test",
                "entity": "orders",
                "enabled": False,
                "filters": []
            }
            post_data = client.http.post(
                '/rules',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            response = client.http.get(f"/rules/{post_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('name'), request_body.get('name'))
            
            client.http.delete(f"/rules/{post_data.get('id')}")
            
            response = client.http.get(f"/rules/{post_data.get('id')}")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json_body.get('error'), 
                             f"Rule with id '{post_data.get('id')}' not found.")
            
    
    def test_delete_not_found(self):
        with Client(app) as client:
            delete_data = client.http.delete(f"/rules/123456")
            
            self.assertEqual(delete_data.status_code, 404)
            self.assertEqual(delete_data.json_body.get('error'), 
                             f"Rule with id '123456' not found.")