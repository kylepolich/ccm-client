.. toctree::
   :maxdepth: 3
   :caption: Contents


The Atlas Cognitive Constallation Manager (CCM) is a software system for centralized, real-time management of a space communication network.  CCM is a solution used adopted by a space communication network as the solution for scheduling access to resources.

CCM follows a client / server model.  The Atlas Network operates the CCM Server software.  The scheduling algorithm that evaluates requests and assigns resources to clients is done server side.  From the client's perspective, the internal operations of the server are not important.  For a deep understanding of how the CCM Server makes scheduling decisions, you may wish to read the "Cognitive Constellation Management, Draft Final Report" prepased by Atlas Space Operations, June 10, 2022.

This guide describes the RESTful API a developer can use to interact with the CCM Server for the purposes of updating their mission parameters and configuration.  

This document's purpose is to explain the process of interacting with the CCM Server.

There are several operations a client may want to execute via the API:

1. Submit an Exact Request

2. Initializing or updating the configurations of your scheduling needs

3. Retrieve details about a Schedule

4. Change your Preference Profile to reflect a change in mission objectives

Each of these operations is described in detail (with code examples) in the sections that follow.

.. include ./license.rst


==================
Using Client
==================


Client Setup
------------

The `ccm-client` Python library is a helper class to facilitate easy integration with the Atlas CCM REST API.

To get started, you will need:

1. A CCM Server **Host** endpoint to connect to
2. An assigned **user_id**
3. A **USER_ACCESS_TOKEN** to identify your account

It is recommended that you place your **USER_ACCESS_TOKEN** in an environmental variable (or .env file), but it can also be passed as a parameter to the `CcmApi` class.

The code snippet below is useful for verifying your local setup.

.. code-block:: python
    :caption: Verify your version and server connection
    :linenos:

	from src.ccm.api import CcmApi

    client = CcmApi('my user id')
    client_version = client.get_version()
    server_version = client.get_server_version()
    preference_profile = client.get_current_profile()
    resp = {
        'client_version': client_version,
        'server_version': server_version,
        'preference_profile': preference_profile
    }
    print(resp)


.. literalinclude:: outputs/verify.json

The above snippet runs three lookup methods and prints the results of each.

`client_version` is the version of your local python library.  If it's behind the latest version, we recommend you upgrade.

`server_version` is the version of the CCM Server you are connected to.  It may be useful for debugging or confirming that you can connect to the server successfully.

`preference_profile` will be a string initially set to "default".  It's functionality is described inline below.

Installing the Python Library
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

TODO: Ok to add to pypi?

Using Protobuf Objects
^^^^^^^^^^^^^^^^^^^^^^

TODO: explain and reference the schedule.proto as a hyperlink



Submitting an Exact Request
---------------------------

Traditional approaches to scheduling often involve placing the cognitive burden on the end user to select a particular Visibility they want to utilize for communication.  An **exact request** like this prevents CCM from assisting with any automated triaging should the chosen Visibility not be available.  However, to provide robust client support, a legacy style exact request can be submitted in the following way.

.. code-block:: python
    :caption: Submit an Exact Request
    :linenos:

	from datetime import datetime
	from src.ccm.api import CcmApi

    client = CcmApi('my user id')
    norad_id = 'test'
    ground_site_id = 's1'
    start_timestamp = int(datetime.fromtimestamp(2022, 1, 1, 11, 50, 0).timestamp())
    end_timestamp   = int(datetime.fromtimestamp(2022, 1, 1, 11, 50, 5).timestamp())
    r = client.create_exact_request(norad_id, ground_site_id, start_timestamp, end_timestamp)
    assert r['success']
    print(r)


.. literalinclude:: outputs/create_exact_request.json


Retrieving Schedules
--------------------

Every run of CCM creates a new unique `schedule_id` representing the most up-to-date version of the future schedule for the network *at the time* of it's generation.  Typically, a `schedule_id` is a random string.

Note
    The Schedule returned will include only Tasking data for the requesting user.  A single user can operate many Spacecraft via the API under a single user account.  Tasks assigned to other users will not be visible in the response.

As a convenience, you may set `schedule_id='latest'` to retrieve the latest Schedule at any given time.  Unlike all other values of `schedule_id`, the value of `latest` is not immutable.  It will change to reflect the current schedule.

.. code-block:: python
    :caption: Retrieving the latest Schedule
    :linenos:

    from src.ccm.api import CcmApi

    client = CcmApi('my user id')
    schedule_id = 'latest'
    resp = client.get_schedule_by_id(schedule_id)
    sch = resp['schedule']

In the previous section, a demonstration was provided that updated User Preferences.  An inspection of the response would reveal it contains a `next_schedule_id`.  Querying immediately for this value will likely result in a failure.  CCM recalculates schedules on a regular time interval.  When the next recalculation begins, it will reflect the updated User Preferences.  When the calculation of that future schedule is completed, it will be assign the provided identifier value.

The code snippet below demonstrates the use of polling when retreving

.. code-block:: python
    :caption: Retrieving a specific Schedule
    :linenos:

    from src.ccm.api import CcmApi

    client = CcmApi('my user id')
    schedule_id = 'server_provided_next_schedule_id_value'
    resp = client.get_schedule_by_id(schedule_id)
    while not(resp['ready']):
        time.sleep(60)
        resp = client.get_schedule_by_id(schedule_id)
    sch = resp['schedule']


Working with User Preferences
-----------------------------

A key data structure in CCM relies on to understand client goals is the User Preference object.  The snippet below provides a demonstration of how to create such an object.  Note that the `upref` created is only a temporary object.  The `generate_user_preference` only helps with the creation of this object.  After completing this step, we will demonstrate saving.

How to generate a new User Preference object

.. code-block:: python

	from src.ccm.api import CcmApi
	from src import schedule_pb2 as objs
    
    tgauss = objs.UserPreference.ConstraintType.TruncatedGaussian
    min_per_day = objs.UserPreference.Objective.ContactMinutesPerDay
    client = CcmApi('my user id')
    upref = client.generate_user_preference(tgauss, min_per_day, mu=60, sigma=10, min=45, max=120)
    assert type(upref) == objs.UserPreference


Saving that object to the `default` Preference Profile

.. code-block:: python

    profile_name = 'default'
    upref = client.generate_user_preference(tgauss, min_per_day, mu=60, sigma=10, min=45, max=120)
    r = client.add_preference_to_profile(profile_name, upref)
    assert r['success']


How to retrieve all preferences

.. code-block:: python

	uprefs = client.get_user_preferences()
	for pref in uprefs:
		print(pref.objective, pref.constraint_type)



Using Preference Profiles
-------------------------

List all Preference Profiles

.. code-block:: python

	profiles = client.get_all_profiles()
	for profile in profiles:
		print(profile.name)


How to create a Preference Preference

.. code-block:: python

	from src.ccm.api import CcmApi

    client = CcmApi('my user id')
	resp = client.create_preference_profile('my new profile')
	assert resp['success']


How to change a Preference Profile

.. code-block:: python

    profile_name = 'my new profile'
    _ = client.add_preference_to_profile(profile_name, upref)
    upref = client.generate_user_preference(tgauss, min_per_day, mu=60, sigma=10, min=45, max=120)

.. A library known as `ccmcore` contains the core logic, data structures, algorithms, unit tests, and other software components to deliver the services described in the "CCM Final Report".

.. A module known as `api` introduces a RESTful API wrapper for the core library.  Via the API, customers of a space communication system scheduled using CCM can make all necessary updates to accomodate their needs.

.. ccm_api uses python 3.3 or newer, so first [create a pytho3n virtualenv](https://docs.python.org/3/library/venv.html) and activate it.

.. TODO: atlas_api installation


you did it in freedom
	assumes visibilities and sats
	assumes knowledge of sites

data comes from freedom
freedom software produces input
outside the scope of CCM, but mandatory req to run


delete a pref from a profile

.. from env vars
.. working with sats
.. working with sites
.. working with overrides
.. working with Tasks and TaskRequests
.. Getting metrics in real time with MQTT


.. include:: source/src.ccm.rst


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`
