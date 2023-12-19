import json
from app import app
from chalice.test import Client
from tests.test_base import TestBase
from tests import db
from rules_system.models import Payment


class TestPayment(TestBase):

    def test_payment_table(self):
        payment = Payment(
            id=123,
            data={
                "client": "Py Test"
            },
        )
        db.add(payment)
        db.commit()

        result = db.query(Payment).all()
        assert len(result) > 0
        assert result[0].data.get('client') == 'Py Test'
        
    
    def test_post_success(self):
        with Client(app) as client:
            request_body = {
                "client": "Py Test"
            }
            response = client.http.post(
                '/payments',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            self.assertEqual(response.status_code, 201)
            self.assertEqual(response.json_body.get('data'), request_body)
            
            
    def test_get_success(self):
        with Client(app) as client:
            request_body = {
                "client": "Py Test"
            }
            post_data = client.http.post(
                '/payments',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            get_data = client.http.get(f"/payments/{post_data.get('id')}")
            
            self.assertEqual(get_data.status_code, 200)
            self.assertEqual(get_data.json_body, request_body)
            

    def test_get_not_found(self):
        with Client(app) as client:
            response = client.http.get(f"/payments/123456")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json_body.get('error'), 
                             "Payment with id '123456' not found.")
            
    
    def test_put_success(self):
        with Client(app) as client:
            request_body = {
                "client": "Py Test"
            }
            post_data = client.http.post(
                '/payments',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            self.assertEqual(post_data.get('data'), request_body)
            
            request_body['client'] = 'Test Py'
            client.http.put(
                f"/payments/{post_data.get('id')}",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
            
            response = client.http.get(f"/payments/{post_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body.get('client'), 'Test Py')
            
            
    def test_put_not_found(self):
        with Client(app) as client:
            request_body = {
                "client": "Py Test"
            }
            put_data = client.http.put(
                f"/payments/123456",
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            )
                        
            self.assertEqual(put_data.status_code, 404)
            self.assertEqual(put_data.json_body.get('error'), 
                             "Payment with id '123456' not found.")
            
    
    def test_delete_success(self):
        with Client(app) as client:
            request_body = {
                "client": "Py Test"
            }
            post_data = client.http.post(
                '/payments',
                headers={'Content-Type':'application/json'},
                body=json.dumps(request_body)
            ).json_body
            
            response = client.http.get(f"/payments/{post_data.get('id')}")
            
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.json_body, request_body)
            
            client.http.delete(f"/payments/{post_data.get('id')}")
            
            response = client.http.get(f"/payments/{post_data.get('id')}")
            self.assertEqual(response.status_code, 404)
            self.assertEqual(response.json_body.get('error'), 
                             f"Payment with id '{post_data.get('id')}' not found.")
            
    
    def test_delete_not_found(self):
        with Client(app) as client:
            delete_data = client.http.delete(f"/payments/123456")
            
            self.assertEqual(delete_data.status_code, 404)
            self.assertEqual(delete_data.json_body.get('error'), 
                             f"Payment with id '123456' not found.")