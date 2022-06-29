import argparse
import logging
import os
import sys

from src.ccm import __version__
from src import schedule_pb2 as objs

__author__ = "Kyle Polich"
__copyright__ = "Atlas Space Operations"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class CcmApi(object):


    def __init__(self, user_id, api_host=None):
        # TODO: authentication
        self.user_id = user_id
        if api_host is None:
            from dotenv import load_dotenv
            load_dotenv(override=True)
            self.api_host = os.getenv('API_HOST')
        else:
            self.api_host = api_host
        self.profiles = {
            'default': {}
        }
        self.current_profile = 'default'


    def get_version(self):
        return "v1.0.0"


    def get_api_host(self):
        return self.api_host


    def get_current_profile(self):
        return self.current_profile


    def get_schedule_by_id(self, id: str) -> objs.Schedule:
        if id == 'empty':
            return objs.Schedule()
        else:
            raise Exception('No schedule by that ID')


    def create_user_preference(self, constraint_type: objs.UserPreference.ConstraintType, objective: objs.UserPreference.Objective, **kwargs):
        if constraint_type == objs.UserPreference.ConstraintType.TruncatedGaussian:
            for req in ['mu', 'sigma']:
                if req not in kwargs:
                    raise Exception(f'Gaussian Requires {req}')
        up = objs.UserPreference(
            constraintType=constraint_type,
            objective=objective
        )
        return up
        #     enum Objective {
        #         AverageMinutesBetweenContacts = 1;
        #         AverageMinutesContactLength   = 2;
        #         MinimumMinutesContactLength   = 4;
        #         ContactMinutesPerDay          = 5;
        #         MaximumMinutesBetweenContacts = 6;
        #         ContactCountPerDay            = 7;
        #         MinimumMinutesBetweenContacts = 8;
        #         MaximumCumuBufferFillPercent  = 9;
        #         FractionHasBand               = 10; // <- New objective for the fraction of tasks that should contain the band
        #         EpochTimeStart                = 11;
        #         ExpectedWaitTime              = 12;
        #         MeanMidpointWithinVisibility  = 13;
        #         OrbitFrequency                = 14;
        #         AoiLatency                    = 15;
        #     }

        #     required ConstraintType constraintType = 1;
        #     required Objective objective = 2;
        #     optional string userId = 4;
        #     optional string label = 5;

        #     optional double mu = 6;
        #     optional double sigma = 7;
        #     optional double min = 8;
        #     optional double max = 9;

        #     optional double start = 10;
        #     optional double decayBegins = 11;
        #     optional double lambdaParam = 12;
        #     optional int32 decayHorizon = 33;

        #     optional double bias = 13;
        #     optional double shape = 14;

        #     optional double weight = 15 [default = 1.0];

        #     required int32 tier = 16 [default = 1];

        #     optional int64 start_time = 17;
        #     optional int64 end_time = 18;

        #     optional VisibilityProperty.VisibilityPropertyType vtype = 19;
        #     optional string vtype_value = 20;
        #     optional string vtype_svalue = 21;

        #     optional double eventsPerHour = 22;
        #     optional string unique_id = 23;
        #     repeated string siteIds = 24;
        #     repeated string noradIds = 25;


    def add_preference_to_profile(self, profile_name, up: objs.UserPreference):
        p = self.profiles[profile_name]
        if 'prefs' not in p:
            self.profiles[profile_name]['prefs'] = []
        self.profiles[profile_name]['prefs'].append(up)
        return {
            'success': True
        }


    def create_preference_profile(self, profile_name):
        if profile_name in self.profiles:
            return {
                'success': False,
                'msg': 'Already exists'
            }
        self.profiles[profile_name] = {}
        return {
            'success': True
        }


    def set_profile(self, profile_name):
        if profile_name not in self.profiles:
            return { 'success': False, 'msg': f'Cannot find {profile_name}' }
        self.current_profile = profile_name
        return { 'success': True }


    def delete_profile(self, profile_name):
        if profile_name not in self.profiles:
            return {
                'success': False,
                'msg': f'Cannot find {profile_name}'
            }
        else:
            del self.profiles[profile_name]
            return {
                'success': True
            }


