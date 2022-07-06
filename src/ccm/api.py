import argparse
import logging
import os
import random
import requests
import sys
import time
import uuid
from google.protobuf.json_format import MessageToDict
from src.ccm import __version__
from src import schedule_pb2 as objs

__author__ = "Kyle Polich"
__copyright__ = "Atlas Space Operations"
__license__ = "MIT"

_logger = logging.getLogger(__name__)


class CcmApi(object):
    "The CcmApi helper class contains several high level functions for controlling the Schedule Tasks assigned to your satellites.  This library manages the REST API calls and provides the user with discrete actions rather than transactional changes."


    def __init__(self, user_id, api_host=None):
        """When initializing this helper object, provide the `user_id` assigned to you when you were granted access to CCM.

        :param user_id: The unique identifier assigned to your user account
        :type user_id: string
        :param api_host: Optional string specifying the CCM Server to use.  If not provided, the ``API_HOST`` environment variable will be used.
        :type api_host: string
        """
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
        """Get the version information of the server you are connecting to.

        :return: A dictionary containing ``version`` identifier
        :rtype: dict
        """
        r = requests.get(self.api_host)
        return {
            "version": "v1.0.0"
        }


    def get_api_host(self):
        """Get the CCM Server API base endpoint the client is communicating with.  This is useful for confirming if you are pointing to a test or production server.

        :return: Return the ``api_host`` of the CCM Server
        :rtype: string
        """
        return self.api_host


    def get_current_profile(self):
        """New users are assigned to the 'default' profile.  Users can add additional preference profiles and switch between them (with other methods of this class).  This function retrieves the currently selected profile.

        :return: The active Preference Profile's identifier
        :rtype: string
        """
        return self.current_profile


    def get_all_profiles(self):
        """Retrieve all the profiles in your user account.

        :return: A list of profiles, as seen in the response in Section `Retrieve All Preference Profiles`_
        :rtype: list
        """
        if self.user_id == 'test':
            return [ {"name": "default"}, {"name": "my new profile"}, {"name": "recovery_mode"} ]
        else:
            return [ { "name": "default" } ]


    def get_profile(self, profile_name='default'):
        """Retrieve a profile from your account which contains all the UserPreference objects in the profile.

        :param profile_name: The unique identifier of the Preference Profile
        :type profile_name: string
        
        :return: A dictionary with Preference Profile details such as those seen in Section `Retrieve A Preference Profile`_
        :rtype: object
        """
        if self.user_id == 'test' and profile_name == "my new profile":
            tgauss_upref = objs.UserPreference(
                constraintType=objs.UserPreference.ConstraintType.TruncatedGaussian,
                objective=objs.UserPreference.Objective.ContactCountPerDay,
                mu=5,
                sigma=2,
                min=0,
                max=20)
            tgu = MessageToDict(tgauss_upref, preserving_proto_field_name=True)
            prefs = [tgu]
            return {
                "name": profile_name,
                "prefs": prefs
            }
        else:
            return {}



    def get_user_preferences(self, profile_name='default') -> list:
        """Retrieve all the UserPreferences found in the given ``profile_name``

        :param profile_name: The unique identifier issued by the server.
        :type profile_name: string
        :return: A Schedule object
        :rtype: Schedule
        """
        return []


    def get_schedule_by_id(self, schedule_id: str) -> objs.Schedule:
        """Retrieve a schedule from the API by id.

        :param schedule_id: The unique identifier issued by the server.
        :type schedule_id: string
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
            for i in range(2):
                s = int(time.time()) + int(random.random() * 60)
                dur = 5 * 60
                vid += 1
                tid += 1
                task = objs.ScheduledTask(
                    taskId=f't{tid}',
                    userId=self.user_id,
                    start=s,
                    end=s+dur,
                    visibilityId=str(vid),
                    noradId=norad_id,
                    siteId='site-a'
                )
                tasks.append(task)
            return objs.Schedule(
                scheduleRunId=schedule_id,
                tasks=tasks,
                score=1.0 # TODO: should we even expose this?
            )
        else:
            raise Exception('No schedule by that ID')


    def create_exact_request(self, norad_id: str, ground_site_id: str, start_timestamp: int, end_timestamp: int):
        """Helper function for creating a UserPreference Object.

        :param norad_id: The NORAD ID of the Spacecraft for which the Exact Request is being made
        :type norad_id: string
        :param ground_site_id: The Ground Site ID for which the Exact Request is being made
        :type ground_site_id: string
        :param start_timestamp: Posix timestamp for the start of the Exact Request
        :type start_timestamp: int
        :param end_timestamp: Posix timestamp for the end of the Exact Request
        :type start_timestamp: int
        :param norad_id: The NORAD ID of the Spacecraft for which the Exact Request is being made
        :type norad_id: int

        :return: A JSON dictionary which should include ``success``
        :rtype: dict
        """
        if norad_id == 'test':
            return {
                'success': True,
                'next_schedule_id': 'example'
            }
        return {
            'success': False,
            'msg': 'Not available'
        }


    def generate_user_preference(self, constraint_type, objective, **kwargs):
        """Helper function for creating a UserPreference Object.

        :param constraint_type: TruncatedGaussian, Logistic, Decay
        :type constraint_type: UserPreference.ConstraintType
        :param objective: One of AverageMinutesBetweenContacts, AverageMinutesContactLength, MinimumMinutesContactLength, ContactMinutesPerDay, MaximumMinutesBetweenContacts, ContactCountPerDay, MinimumMinutesBetweenContacts, MaximumCumuBufferFillPercent, FractionHasBand, EpochTimeStart, ExpectedWaitTime, MeanMidpointWithinVisibility, OrbitFrequency, AoiLatency
        :type objective: UserPreference.Objective
        :param weight: A value representing how much emphasis to give to this UserPreference relative to others.
        :type weight: float
        :param mu: Required for ConstraintType.TruncatedGaussian
        :type mu: float
        :param sigma: Required for ConstraintType.TruncatedGaussian
        :type sigma: float
        :param min: Required for ConstraintType.TruncatedGaussian
        :type min: float
        :param max: Required for ConstraintType.TruncatedGaussian
        :type max: float

        :param bias: Required for ConstraintType.Logistic
        :type bias: float
        :param shape: Required for ConstraintType.Logistic
        :type shape: float

        :param start: Required for ConstraintType.Decay
        :type start: float
        :param decayBegins: Required for ConstraintType.Decay
        :type decayBegins: float
        :param lambdaParam: Required for ConstraintType.Decay
        :type lambdaParam: float
        :param decayHorizon: Required for ConstraintType.Decay
        :type decayHorizon: int32

        :return: A validated UserPreference object such as the example in Section `Retrieve All Preference Profiles`_
        :rtype: UserPreference
        """
        mu = None
        sigma = None
        mmin = None
        mmax = None
        if constraint_type == objs.UserPreference.ConstraintType.TruncatedGaussian:
            for req in ['mu', 'sigma']:
                mu = float(kwargs['mu'])
                sigma = float(kwargs['sigma'])
                if 'min' in kwargs:
                    mmin = float(kwargs['min'])
                if 'max' in kwargs:
                    mmax = float(kwargs['max'])
                if req not in kwargs:
                    raise Exception(f'Gaussian Requires {req}')
        up = objs.UserPreference(
            userId=self.user_id,
            tier=1,
            mu=mu,
            sigma=sigma,
            min=mmin,
            max=mmax,
            constraintType=constraint_type,
            objective=objective
        )
        return up

        #     optional string label = 5;

        #     optional VisibilityProperty.VisibilityPropertyType vtype = 19;
        #     optional string vtype_value = 20;
        #     optional string vtype_svalue = 21;
        #     optional double eventsPerHour = 22;
        #     repeated string siteIds = 24;
        #     repeated string noradIds = 25;


    def add_preference_to_profile(self, profile_name, upref: objs.UserPreference):
        """Add the ``upref`` to the Preference Profile identified as ``profile_name``

        :param profile_name: The unique identifier of the Preference Profile
        :type profile_name: string
        :return: A dictionary with ``success`` value (i.e. ``{ "success": True }``)
        :rtype: dict
        """
        p = self.profiles[profile_name]
        if 'prefs' not in p:
            self.profiles[profile_name]['prefs'] = []
        self.profiles[profile_name]['prefs'].append(upref)
        return {
            'success': True
        }


    def create_preference_profile(self, profile_name):
        """Retrieve a schedule from the API by id.

        :param profile_name: The unique identifier of the Preference Profile
        :type profile_name: string
        :return: A dictionary with ``success`` value
        :rtype: dict
        """
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
        """Retrieve a schedule from the API by id.

        :param profile_name: The unique identifier of the Preference Profile
        :type profile_name: string
        :return: A dictionary with ``success`` value
        :rtype: dict
        """
        if profile_name not in self.profiles:
            return { 'success': False, 'msg': f'Cannot find {profile_name}' }
        self.current_profile = profile_name
        return {
            'success': True,
            'next_schedule_id': str(uuid.uuid4())
        }


    def delete_profile(self, profile_name):
        """Retrieve a schedule from the API by id.

        :param profile_name: The unique identifier of the Preference Profile
        :type profile_name: string
        :return: A dictionary with ``success`` value
        :rtype: dict
        """
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


