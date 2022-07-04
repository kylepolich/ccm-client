from src.ccm.api import CcmApi
from docs.outsrc.verify import get_results as verify_get_results
from google.protobuf.json_format import MessageToDict
import json


def create_verify_output(client):
    result = verify_get_results(client) 
    fn = 'docs/outputs/verify.json'
    json.dump(result, open(fn, 'w'), indent=4, sort_keys=True)


def create_exact_request(client):
    s = 0
    e = 60*5
    resp = client.create_exact_request('test', '12345', s, e)
    fn = 'docs/outputs/create_exact_request.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


def create_schedule_request(client):
    resp = client.get_schedule_by_id('example')
    fn = 'docs/outputs/create_schedule_request.json'
    o = MessageToDict(resp, preserving_proto_field_name=True)
    json.dump(o, open(fn, 'w'), indent=4, sort_keys=True)



client = CcmApi('test')
create_verify_output(client)
create_exact_request(client)
create_schedule_request(client)