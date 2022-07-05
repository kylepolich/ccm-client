.. toctree::
   :maxdepth: 3
   :caption: Contents


Introduction
-------------------------


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

A keen reader may notice that the CCM API *does not* provide support for any of the following actions:

#. Add a new Spacecraft (i.e. unique ``norad_id``) to the system

#. Add a new Ground Site

#. Update Visibilities


**Atlas Freedom Integration**

CCM is a complementary system to *Atlas Freedom*.  Data about Spacecraft and Visibilities are managed via *Atlas Freedom*, which will send appropriate data to CCM for Schedules to be produced.



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

To leverage the Python helper library described in this document, there are serveral options for installation.  To install the library locally so that you can import it into your code, use the command shown below.

.. code-block:: bash

    pip install -e https://github.com/atlas/ccm-client.git


To clone the repository's source code directly, use the command below.

.. code-block:: bash

    git clone https://github.com/atlas/ccm-client.git


Using Protobuf Objects
^^^^^^^^^^^^^^^^^^^^^^

CCM leverages `Protocol Buffers <https://developers.google.com/protocol-buffers>` (aka ``protobuf``) to define a polyglot schema of the objects sent to and returned from CCM.  Several of the functions provided by the library return Protobuf objects.

To answer schema related questions about the objects returned, we recommend you refer directly to the ``schedule.proto`` object definition file.



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

This response confirms the request was successful and includes `next_schedule_id` which a unique identifier that can be used to retrieve the Schedule that will be built in reflecting your request.  See the next section for details on retreiving the Schedule.


Retrieving Schedules
--------------------

Every run of CCM creates a new unique `schedule_id` representing the most up-to-date version of the future schedule for the network *at the time* of it's generation.  Typically, a `schedule_id` is a random string.

Note
    The Schedule returned will include only Tasking data for the requesting user.  A single user can operate many Spacecraft via the API under a single user account.  Tasks assigned to other users will not be visible in the response.

As a convenience, you may set `schedule_id='latest'` to retrieve the latest Schedule at any given time.  Unlike all other values of ``schedule_id``, the value of `latest` is not immutable.  It will change to reflect the current schedule.

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
    schedule_id = 'example'
    resp = client.get_schedule_by_id(schedule_id)
    while not(resp['ready']):
        time.sleep(60)
        resp = client.get_schedule_by_id(schedule_id)
    sch = resp['schedule']

When the Schedule is eventually generated and available, it could look like the example shown below.  In this minimal example, there are two Tasks for the requesting user.  Both are on the same Spacecraft and same Ground Site.  The particular ``visibilityId`` found in *ATLAS Freedom* will be included for reference.

.. literalinclude:: outputs/create_schedule_request.json


Working with User Preferences
-----------------------------

A key data structure in CCM relies on to understand client goals is the User Preference object.  The snippet below provides a demonstration of how to create such an object.  Note that the `upref` created is only a temporary object.  The `generate_user_preference` only helps with the creation of this object.  After completing this step, we will demonstrate saving.

The latest version of CCM supports three mathematical functions or **Objectives** which can be used to express your preference over different values.

#. Truncated Gaussian
#. Logistic
#. Decay


Truncated Gaussian Preference
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The most popular Objective function is the *Truncated Gaussian*.  It is visualized in the image below.  It requires parameters ``mu`` and ``sigma`` which define the mean and variance of the curve.  It helpful to think of the ``mu`` parameter as the ideal value you'd like to get.  The ``sigma`` value expresses your flexibility in accepting values that are close to, but not precisely, your value of ``mu``.  Optionally, a ``min`` and ``max`` value can be provided.

.. image:: imgs/constraint-type-gaussian.png
    :scale: 50%
    :align: center

.. code-block:: python
    :caption: How to generate a new Gaussian User Preference object
    :linenos:

	from src.ccm.api import CcmApi
	from src import schedule_pb2 as objs
    
    tgauss = objs.UserPreference.ConstraintType.TruncatedGaussian
    min_per_day = objs.UserPreference.Objective.ContactCountPerDay
    client = CcmApi('my user id')
    tgauss_upref = client.generate_user_preference(tgauss, min_per_day, mu=5, sigma=2, min=0, max=20)
    assert type(tgauss_upref) == objs.UserPreference



Logistic Preference
^^^^^^^^^^^^^^^^^^^

The Logistic Preference requres two parameters: ``bias`` and ``shape``.  We recommend readers review the `Logistic function <https://en.wikipedia.org/wiki/Logistic_function>` wikipedia page to ensure you have sufficient background in the mathematical definition of the Logistic function.  In their documentation, *L = bias* and *k = shape*.

This Objective shape is commonly choosen to express a "soft max" constraint in which the user would be happy to get an unlimited amount of some value (e.g. Minutes per Day), but finds diminishing returns after a certain point.

.. image:: imgs/constraint-type-logistic.png
    :scale: 50%
    :align: center

.. code-block:: python
    :caption: How to generate a new Logistic User Preference object
    :linenos:

    from src.ccm.api import CcmApi
    from src import schedule_pb2 as objs
    
    logistic = objs.UserPreference.ConstraintType.Logistic
    min_per_day = objs.UserPreference.Objective.ContactMinutesPerDay
    client = CcmApi('my user id')
    logistic_upref = client.generate_user_preference(logistic, min_per_day, bias=10, shape=2)
    assert type(logistic_upref) == objs.UserPreference




Decay Preference
^^^^^^^^^^^^^^^^

There are some situations in which a satellite operator may be open to accepting any values in a certain range, followed by a steep decline in utility after the range has ended.  To capture preferences of this nature, we offer the Decay Preference which is illustrated in the image below.  The ``start`` parameter defines the lowest value for which the metric is acceptable.  The ``decayBegins`` must be greater than or equal to ``start``, and represents the time at which the appear of values begins to decline.  The ``lambdaParam`` is used as a decay parameter which describes the decline in perceived value as the observed value continues to increase up until ``decayHorizon``, beyond which all observed values have no value.

.. image:: imgs/constraint-type-decay.png
    :scale: 50%
    :align: center

.. code-block:: python
    :caption: How to generate a new Decay User Preference object
    :linenos:

    from src.ccm.api import CcmApi
    from src import schedule_pb2 as objs
    
    decay = objs.UserPreference.ConstraintType.Decay
    min_per_day = objs.UserPreference.Objective.ContactCountPerDay
    client = CcmApi('my user id')
    decay_upref = client.generate_user_preference(decay, min_per_day, start=0, decayBegins=5, lambdaParam=5, decayHorizon=20)
    assert type(decay_upref) == objs.UserPreference


Saving User Preferences to Profiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The previous three sections defined unique variables ending in ``_upref`` which collectively may fully describe the mission goals of a particular user.  They can be saved to a common Preference Profile (the *default* profile in the example below) via the ``add_preference_to_profile`` function.

.. code-block:: python
    :caption: Saving that objects generated above to the `default` Profile
    :linenos:

    profile_name = 'default'
    r = client.add_preference_to_profile(profile_name, tgauss_upref)
    r = client.add_preference_to_profile(profile_name, logistic_upref)
    r = client.add_preference_to_profile(profile_name, decay_upref)
    assert r['success']





Using Preference Profiles
-------------------------

A *Preference Profile* is a user defined collection of User Preference objects.  By default, all CCM users have a *default* Preference Profile.  Users can create alternate Preference Profiles and add unique User Preferences to them.  Should mission objectives change, the use can elect to change their active profile to one of their custom Preference Profiles.  Once a change has been submitted to the API (as demonstrated below), the next Schedule generated will reflect the User Preferences in the newly activated profile.  Should a user choose to take advantage of having more Preference Profiles, this section covers the process of creating, listing, updating, activating, and removing Preference Profiles.

Create a Preference Profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^

The code snippet below demonstrates the process for creating a Preference Profile which will be identified with the unique name ``my new profile``.

.. code-block:: python
    :caption: How to create a Preference Preference
    :linenos:

    from src.ccm.api import CcmApi

    client = CcmApi('my user id')
    resp = client.create_preference_profile('my new profile')
    assert resp['success']


Update a Preference Profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Once a Preference Profile is created, new User Preference can be generated and added to it.

.. code-block:: python
    :caption: How to create a Preference Preference
    :linenos:

    from src.ccm.api import CcmApi
    from src import schedule_pb2 as objs
    
    tgauss = objs.UserPreference.ConstraintType.TruncatedGaussian
    min_per_day = objs.UserPreference.Objective.ContactCountPerDay
    client = CcmApi('my user id')
    tgauss_upref = client.generate_user_preference(tgauss, min_per_day, mu=5, sigma=2, min=0, max=20)
    profile_name = 'my new profile'
    r = client.add_preference_to_profile(profile_name, tgauss_upref)
    assert r['success']


Activating a Preference Profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A CCM user always has an active Preference Profile which begins as *default*.  The active Preference Profile cannot be deleted.  Users can change which profile is active at any time.

.. code-block:: python
    :caption: How to change a Preference Profile
    :linenos:

    profile_name = 'my new profile'
    resp = client.set_profile(profile_name)
    assert r['success']
    assert 'next_schedule_id' in r

Since a change in profile is likely to result in a new set of Task assignments, CCM will return a ``next_schedule_id`` in the response which indicates the next Schedule which will reflect the newly activated profile.


Retrieve All Preference Profiles
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

To get a list of all the created Preference Profiles, follow the example shown below.

.. code-block:: python
    :caption: How to retrieve all preferences
    :linenos:

	profiles = client.get_all_profiles()
	for profile in profiles:
		print(profile['name'])


Delete a Preference Profile
^^^^^^^^^^^^^^^^^^^^^^^^^^^

For CCM users wishing to remove a deprecated Preference Profile, the snippet below demonstrates the process to hard delete the profile.

.. code-block:: python
    :caption: How to delete a Preference Profile
    :linenos:

    client.set_profile('default')
    resp = client.delete_profile('my new profile')
    assert resp['success']


Python helper functions
-----------------------


.. automodule:: src.ccm.api
   :members:
   :undoc-members:
   :show-inheritance:


.. Indices and tables
.. ==================

.. * :ref:`genindex`
.. * :ref:`modindex`
.. * :ref:`search`


.. aoi ignore, lockout, minimize
.. from env vars
.. working with sats
.. working with sites
.. working with overrides
.. working with Tasks and TaskRequests
.. Getting metrics in real time with MQTT
