from mitmproxy import http
import json
from datetime import datetime
from database.database_connector import FirebaseClient
import os
from mitmproxy import ctx

class Process_accounts:
    def __init__(self):
        parralel_mthd = os.getenv('process_method')
        if parralel_mthd == 'True':
            self.PARRALEL_MTHD = True
        else:
            self.PARRALEL_MTHD = False
        ctx.log('PARRALEL_MTHD: ' + str(self.PARRALEL_MTHD))
        self.OWNER = os.getenv('DSCRD_USER')
        self.OWNER_ID = os.getenv('DSCRD_USER_ID')
        self.fbc = FirebaseClient()
        self.accounts_og = self.fbc.ref_users.child(self.OWNER_ID).child(
            'data').child('accounts_og')
        self.accounts = self.fbc.ref_users.child(self.OWNER_ID).child(
            'data').child('accounts')
        self.account = {
            "password": 'TourneAIO123!',
            "street": None,
            "postcode": None,
            "email": None,
            "customer_id": None,
            "payment_method_id": None,
            "owner": self.OWNER,
            "shipping_address_id": None,
            "billing_address_id": None,
            'first_name': None,
            'last_name': None,
            "shipping_method_id": 159,
            "raffles_entered": [
            ],
            "time_of_token_generation": None,
            "token": None
        }

        ctx.log(f'Logged in as {self.OWNER}')
        os.system(f'title TIGERGEN PROCESS ACCOUNTS INTERFACE - {self.OWNER}')

    def request(self, flow: http.HTTPFlow) -> None:
        def get_headers(origin):
            return {'strict-transport-security': 'max-age=31536000 ; includeSubDomains',
                    'access-control-allow-origin': origin,
                    'access-control-allow-credentials': 'true',
                    'access-control-allow-methods': 'PUT, POST, GET, OPTIONS, DELETE',
                    'access-control-allow-headers': 'Origin, Accept, Content-Type, X-Requested-With, Authorization, Pragma, exj5wzxnuf-a, exj5wzxnuf-a0, exj5wzxnuf-a1, exj5wzxnuf-b, exj5wzxnuf-c, exj5wzxnuf-d, exj5wzxnuf-e, exj5wzxnuf-f, exj5wzxnuf-g, exj5wzxnuf-z',
                    'set-cookie': 'bm_sv=79F5AD4975D895CF2A2E622F49A5B75A~YAAQkioSAqS2jbGCAQAAafCOshCRmwyD9yUDFOefl8xEUhAURqS9Q6sY6NexnZV/55b/PSlP1PljBRwyS82/5Oq+7ieiwRTJHPqOapc0i/dA8UofUHgX1IdfxyKpj2MV2x+DfENByuNUD6dsIuSvdKfS4r0S04NqLsjJNRlHFBRxUpgDJIcpIEHZCxwcrJcL/BbJ7W8X6eNZKrAr5IxmtUtS3MEmGct9QkSBr6JsxPhXB0IxVJLFS9eGqyYfAR82T0K5kWcW~1; Domain=.endclothing.com; Path=/; Expires=Thu, 18 Aug 2022 21:00:37 '}
        url = flow.request.pretty_url
        if flow.request.method != 'OPTIONS':
            if self.PARRALEL_MTHD:
                if url == 'https://api.endclothing.com/customer/rest/v2/gb/account/me' or url == 'https://api2.endclothing.com/gb/rest/V1/end/vault/mine':
                    ctx.log(self.account)
                    flow.request.headers['authorization'] = 'Bearer ' + \
                        self.account['token']
            if url == 'https://api.endclothing.com/customer/rest/v2/gb/email-availability':
                flow.response = http.Response.make(
                    200,
                    r'{"body":{"available":false},"message":{"body":"","translation":{"id":null,"variables":[]}}}',
                    get_headers(flow.request.headers.get('Origin')),
                )
            if url == 'https://api.endclothing.com/customer/rest/v2/gb/customer/token':
                def get_credentials():
                    self.user = list(
                        list(
                            self.accounts_og.order_by_key()
                            .limit_to_first(1)
                                .get()
                                .items())[0])
                    ctx.log(self.user)
                    email = self.user[0]
                    if self.accounts.child(email).get() is not None:
                        self.accounts_og.child(email).delete()
                        get_credentials()
                    password = self.user[1].get('password')
                    if password is None:
                        password = 'TourneAIO123!'
                    return {
                        "email": email.replace(',', '.'),
                        "password": password
                    }
                flow.request.set_text(json.dumps(get_credentials()))
                ctx.log(flow.request.get_text())
    def response(self, flow: http.HTTPFlow) -> None:
        def update_accounts():

            if self.account.get('customer_id') == None or self.account.get('payment_method_id') == None or self.account.get('token') == None:
                return
            self.accounts.child(
                self.account['email']).set(self.account)

            payload = {"code": 401,
                       "message": f"Account data generated! {self.account['email']}"
                       }
            self.accounts_og.child(self.account['email']).delete()
            flow.response.set_text(json.dumps(payload))
            flow.response.status_code = 401
            self.account = {
                "password": 'TourneAIO123!',
                "street": None,
                "postcode": None,
                "email": None,
                "customer_id": None,
                "payment_method_id": None,
                "shipping_address_id": None,
                "billing_address_id": None,
                "owner": self.OWNER,
                'first_name': None,
                'last_name': None,
                "raffles_entered": [
                ]
            }

        url = flow.request.pretty_url
        if flow.request.method != 'OPTIONS':
            if url == "https://api2.endclothing.com/gb/rest/V1/end/vault/mine":
                content = str(flow.response.get_text())
                json_content = json.loads(content)
                self.account['payment_method_id'] = json_content[0]['entity_id']
                update_accounts()

            elif url == "https://api.endclothing.com/customer/rest/v2/gb/account/me":
                content = str(flow.response.get_text())
                json_content = json.loads(content)
                self.account['customer_id'] = json_content['body']['id']
                self.account['email'] = json_content['body']['email'].replace(
                    '.', ',')
                self.account['first_name'] = json_content['body']['first_name']
                self.account['last_name'] = json_content['body']['last_name']
                self.account['shipping_address_id'] = json_content['body']['addresses'][0]['id']
                self.account['billing_address_id'] = json_content['body']['addresses'][0]['id']
                self.account['postcode'] = json_content['body']['addresses'][0]['postcode']
                self.account['street'] = json_content['body']['addresses'][0]['street'][0]
                update_accounts()
            elif url == 'https://api.endclothing.com/customer/rest/v2/gb/customer/token':
                now = datetime.now()
                content = str(flow.response.get_text())
                json_content = json.loads(content)
                try:
                    self.account['token'] = json_content['body']['token']
                except:
                    flow.response.status_code = 401
                    payload = {"error":
                               {"domain": "s_customer", "reason": "VALIDATION_ERROR", "message": {
                                "body": f"Removed broken account {self.user[0]}", "translation": {"id": None, "variables": []}}, "errors": []}}
                    self.fbc.ref_og_accounts.child(self.user[0]).delete()
                    flow.response.set_text(json.dumps(payload))
                self.account['time_of_token_generation'] = now.strftime(
                    "%m/%d/%Y @ %H:%M:%S")
                if self.PARRALEL_MTHD:
                    flow.response.status_code = 401
                    payload = {"error":
                               {"domain": "s_customer", "reason": "VALIDATION_ERROR", "message": {
                                "body": f"Processing account {self.user[0]}", "translation": {"id": None, "variables": []}}, "errors": []}}
                    flow.response.set_text(json.dumps(payload))
                else:
                    update_accounts()

addons = [Process_accounts()]
os.system(f'start /wait cmd /c process_accounts.py')
