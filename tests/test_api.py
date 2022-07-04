import pytest

from src.ccm.api import CcmApi
from src import schedule_pb2 as objs

__author__ = "Kyle Polich"
__copyright__ = "Kyle Polich"
__license__ = "MIT"


def test_main():
    ca = CcmApi('test')
    v = ca.get_version()
    assert v.startswith("v")


def test_get_api_host():
    ca = CcmApi('test')
    assert ca.get_api_host() == 'https://zbikyifgak.execute-api.us-east-1.amazonaws.com/prod/'


def test_get_schedule_not_exists():
    fake_id = 'does-not-exist'
    ca = CcmApi('test')
    try:
        sch = ca.get_schedule_by_id(fake_id)
        assert False
    except:
        pass


def test_get_schedule_success():
    test_id = 'empty'
    ca = CcmApi('test')
    sch = ca.get_schedule_by_id(test_id)
    assert type(sch) == objs.Schedule


def test_generate_user_preference():
    ct = objs.UserPreference.ConstraintType.TruncatedGaussian
    objective = objs.UserPreference.Objective.ContactMinutesPerDay
    ca = CcmApi('test')
    up = ca.generate_user_preference(ct, objective, mu=10, sigma=5)
    assert type(up) == objs.UserPreference


def test_create_preference_profile():
    ca = CcmApi('test')
    resp = ca.create_preference_profile('temp')
    assert resp['success']


def test_delete_profile():
    ca = CcmApi('test')
    resp = ca.create_preference_profile('temp')
    assert resp['success']
    resp = ca.delete_profile('temp')
    assert resp['success']


def test_set_profile():
    ca = CcmApi('test')
    p = ca.get_current_profile()
    assert p == 'default'
    resp = ca.set_profile('does-not-exist')
    assert not(resp['success'])
    resp = ca.create_preference_profile('temp')
    assert resp['success']
    resp = ca.set_profile('temp')
    assert resp['success']
    p = ca.get_current_profile()
    assert p == 'temp'
    resp = ca.delete_profile('temp')
    assert resp['success']


def test_profile():
    ca = CcmApi('test')
    resp = ca.set_profile('does-not-exist')
    assert not(resp['success'])
    resp = ca.create_preference_profile('temp')
    assert resp['success']
    resp = ca.create_preference_profile('temp')
    assert not(resp['success'])
    resp = ca.set_profile('temp')
    assert resp['success']
    ct = objs.UserPreference.ConstraintType.TruncatedGaussian
    objective = objs.UserPreference.Objective.ContactMinutesPerDay
    up = ca.generate_user_preference(ct, objective, mu=10, sigma=5)
    resp = ca.add_preference_to_profile('temp', up)
    assert resp['success']
    resp = ca.delete_profile('temp')
    assert resp['success']


def test_create_exact_request_has_mock():
    ca = CcmApi('test')
    s = 0
    e = 60*5
    resp = ca.create_exact_request('test' '12345', s, e)
    assert resp['success']
    assert 'next_schedule_id' in resp


# def test_
#     TODO: check on the schedule after submitting a change
#     resp = ca.update()
#     assert resp['success']


# TODO: get schedule
# TODO: docstring stuff
# TODO: writing



