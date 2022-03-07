LLEMR Django Settings
=====================

Default settings are loaded from ``config/setttings/demo.py``. Available settings for LLEMR:

OSLER_ABOUT_NAME
----------------

Name of about link in top bar. Default `"About"`.

OSLER_AUDIT_BLACK_LIST
----------------------

List of IP addresses to exclude from audit. Default: `[]`.

OSLER_ATTENDANCE_URL
--------------------

Link that redirects to the attendance page. Can also be set by an environment variable of the same name. Default `https://www.wustl.edu`.

OSLER_DEFAULT_ADDRESS
---------------------

The default address field for new patients. Default: `''`.

OSLER_DEFAULT_APPOINTMENT_HOUR
------------------------------

The default hour for new appointments.

OSLER_DEFAULT_CITY
------------------

The default city for new patients. Default: `''`.

OSLER_DEFAULT_STATE
-------------------

The default state for new patients. Default: `''`.

OSLER_DEFAULT_ZIP_CODE
----------------------

The default ZIP code for new patients. Default: `''`.

OSLER_DEFAULT_COUNTRY
---------------------

The default country for new patients. Default: `''`.

OSLER_CLINIC_DAYS_PER_PAGE
--------------------------

How many clinic days should be shown in the attending-style dashboard. Default `20`.


OSLER_DEFAULT_DASHBOARD
-----------------------

Name of the view to redirect to by default. Default `dashboard-active`.

OSLER_ROLE_DASHBOARDS
---------------------

A mapping of role name to dashboard view name. Default:

.. code-block:: python

	{
    	'Attending': 'dashboard-attending',
	}

OSLER_DEFAULT_ACTIVE_STATUS
---------------------------

Name of the active state of patients. Takes the form of a tuple of `('name', True)`. Default: `('Active', True)`.

OSLER_DEFAULT_INACTIVE_STATUS
-----------------------------

Name of the active state of patients. Takes the form of a tuple of `('name', False)`. Default: `('Inactive', True)`.

OSLER_DISPLAY_REFERRALS
-----------------------

Display referral app features. Default `False`.

OSLER_DISPLAY_APPOINTMENTS
--------------------------

Display appointment app features. Default `False`.

OSLER_DISPLAY_CASE_MANAGERS
---------------------------

Display case manager features. Default `False`.

OSLER_DISPLAY_ATTESTABLE_BASIC_NOTE
-----------------------------------

Display referral app features. Default `False`.

OSLER_DISPLAY_DIAGNOSIS
-----------------------

Display diagnosis. Default `True`.

OSLER_DISPLAY_VOUCHERS
----------------------

Display field for vouchers in H&P style note. Default `False`.

OSLER_DISPLAY_WILL_RETURN
-------------------------

Display will return field in H&P style note. Default `False`.

OSLER_DISPLAY_ATTENDANCE
------------------------

Display link for attendance. Default `False`.

OSLER_DISPLAY_FOLLOWUP
----------------------

Display followup app features. Default `False`.

OSLER_DISPLAY_VACCINE
---------------------

Display vaccine app features. Default `False`.

OSLER_GITHUB_URL
----------------

Link to the github page for this project. May be removed in future releases. Default ``.

OSLER_MAX_APPOINTMENTS
----------------------

Maximum number of allowed appointments per day.

OSLER_MAX_SYSTOLIC
------------------

Maximum allowed systolic blood pressure before an error is triggered.

OSLER_MIN_DIASTOLIC
-------------------

Minimum allowed systolic blood pressure before an error is triggered.

OSLER_TODO_LIST_MANAGERS
------------------------

.. code-block:: python

	OSLER_TODO_LIST_MANAGERS = [
		('core', 'ActionItem'),
		('referral', 'FollowupRequest'),
		('vaccine', 'VaccineActionItem')
	]


OSLER_WORKUP_COPY_FORWARD_FIELDS
--------------------------------

Which fields should be copied forward for H&P style notes ("Workups"). Options include `pmh`, `psh`, `fam_hx`, `soc_hx`, `meds`, `allergies`.

OSLER_WORKUP_COPY_FORWARD_MESSAGE
---------------------------------

A string giving the message should be added to fields copied forward in H&P-style notes.

Default is:

.. code-block:: python

	(u"Migrated from previous workup on {date}. "
     u"Please delete this heading and UPDATE "
     u"the following as necessary:\n\n{contents}")
