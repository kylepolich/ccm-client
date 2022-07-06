from datetime import datetime
from src.ccm.api import CcmApi
import src.schedule_pb2 as objs
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
    resp = MessageToDict(resp, preserving_proto_field_name=True)
    tasks2 = []
    for task in resp['tasks']:
        task['start'] = datetime.fromtimestamp(int(task['start'])).isoformat()
        task['end'] = datetime.fromtimestamp(int(task['end'])).isoformat()
        tasks2.append(task)
    resp['tasks'] = tasks2
    fn = 'docs/outputs/create_schedule_request.json'
    o = resp
    # o = MessageToDict(resp, preserving_proto_field_name=True)
    json.dump(o, open(fn, 'w'), indent=4, sort_keys=True)


def get_all_profiles(client):
    resp = client.get_all_profiles()
    fn = 'docs/outputs/get_all_profiles.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


def get_profile(client):
    resp = client.get_profile("my new profile")
    fn = 'docs/outputs/get_profile.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


def demo_add_preference_to_profile(client):
    resp = client.add_preference_to_profile("default", None)
    fn = 'docs/outputs/add_preference_to_profile.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


def generate_user_preference(client):
    tgauss = objs.UserPreference.ConstraintType.TruncatedGaussian
    count_per_day = objs.UserPreference.Objective.ContactCountPerDay
    resp = client.generate_user_preference(tgauss, count_per_day, mu=5, sigma=2, min=0, max=20)
    fn = 'docs/outputs/generate_user_preference.json'
    o = MessageToDict(resp)
    json.dump(o, open(fn, 'w'), indent=4, sort_keys=True)


def demo_set_profile(client):
    resp = client.set_profile("default")
    fn = 'docs/outputs/set_profile.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


def demo_delete_profile(client):
    resp = client.delete_profile("default")
    fn = 'docs/outputs/delete_profile.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


def demo_create_preference_profile(client):
    profile_name = "my new profile"
    if profile_name in client.profiles:
        del client.profiles[profile_name]
    resp = client.create_preference_profile(profile_name)
    fn = 'docs/outputs/create_preference_profile.json'
    json.dump(resp, open(fn, 'w'), indent=4, sort_keys=True)


client = CcmApi('test')
create_verify_output(client)
create_exact_request(client)
create_schedule_request(client)
get_profile(client)
get_all_profiles(client)
demo_add_preference_to_profile(client)
generate_user_preference(client)
demo_set_profile(client)
demo_delete_profile(client)
demo_create_preference_profile(client)
