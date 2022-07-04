import argparse
import logging
import os
import random
import requests
import sys

from src.ccm import __version__
from src import schedule_pb2 as objs

__author__ = "Kyle Polich"
__copyright__ = "Atlas Space Operations"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class CcmApi(object):
    "CCM API is great"


    def __init__(self, user_id, api_host=None):
        """When initializing this helper object, provide the `user_id` assigned to you when you were granted access to CCM."""
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
        """Get the version information for the client you are running.

        :return: A version identifier
        :rtype: string
        """
        return "v1.0.0"


    def get_server_version(self):
        r = requests.get(self.api_host)
        return {
            "version": "v1.0.0"
        }


    def get_api_host(self):
        """Get the CCM Server API base endpoint the client is communicating with.  This is useful for confirming if you are pointing to a test or production server."""
        return self.api_host


    def get_current_profile(self):
        """New users are assigned to the 'default' profile.  Users can add additional preference profiles and switch between them (with other methods of this class).  This function retrieves the currently selected profile."""
        return self.current_profile


    def get_all_profiles(self):
        return []


    def get_user_preferences(self, profile_name='default') -> list:
        """Retrieve a list of UserPreference objects applicable to the current user."""
        return []


    def get_schedule_by_id(self, schedule_id: str) -> objs.Schedule:
        """Retrieve a schedule from the API by id.

        :param schedule_id: The unique identifier issued by the server.
        :raises Exception: No schedule by that ID.
        :return: A Schedule object
        :rtype: Schedule
        """
        if schedule_id == 'empty':
            return objs.Schedule()
        elif schedule_id == 'example':
            tasks = []
            norad_id = '55555'
            vid = random.randint(1000,2000)
            tid = random.randint(100,200)
            for i in range(5):
                s = int(time.time()) + int(random.random() * 60)
                dur = 5 * 60
                vid += 1
                tid += 1
                task = objs.ScheduledTask(
                    taskId=f't{tid}',
                    userId=self.user_id,
                    start=s,
                    end=start+dur,
                    visibilityId=vid,
                    noradId=norad_id,
                    siteId='site-a'
                )
                tasks.append(task)
            tasks = [task1, task2]
            return objs.Schedule(
                scheduleRunId=1,
                tasks=tasks,
                score=1.0 # TODO: should we even expose this?
            )
        else:
            raise Exception('No schedule by that ID')


    def get_ground_sites(self):
        """Retrieve a list of the Ground Sites available in the network which the client can request usage of."""
        return []


    def create_exact_request(self, norad_id: str, ground_site_id: str, start_timestamp: int, end_timestamp: int):
        if norad_id == 'test':
            return {
                'success': True,
                'next_schedule_id': 'example'
            }
        return {
            'success': False,
            'msg': 'Not available'
        }


    def generate_user_preference(self, constraint_type: objs.UserPreference.ConstraintType, objective: objs.UserPreference.Objective, **kwargs):
        """Helper function for creating a UserPreference Object.

        :param constraint_type: TruncatedGaussian, Logistic, Decay
        :type constraint_type: UserPreference.ConstraintType
        :param objective: See UserPreference.Objective
        :type objective: UserPreference.Objective
        :param weight: A value representing how much emphasis to give to this UserPreference relative to others.
        :type weight: float
        :param mu: For TruncatedGaussian(, optional)
        :type mu: float
        :param sigma: For TruncatedGaussian(, optional)
        :type sigma: float
        :param min: For TruncatedGaussian(, optional)
        :type min: float
        :param max: For TruncatedGaussian(, optional)
        :type max: float
        :return: A validated UserPreference object
        :rtype: UserPreference
        """
        if constraint_type == objs.UserPreference.ConstraintType.TruncatedGaussian:
            for req in ['mu', 'sigma']:
                if req not in kwargs:
                    raise Exception(f'Gaussian Requires {req}')
        up = objs.UserPreference(
            userId=self.user_id,
            tier=1,
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

        #     optional string label = 5;

        #     optional double start = 10;
        #     optional double decayBegins = 11;
        #     optional double lambdaParam = 12;
        #     optional int32 decayHorizon = 33;

        #     optional double bias = 13;
        #     optional double shape = 14;

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


