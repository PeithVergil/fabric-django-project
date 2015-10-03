"""
Tasks for automating the setup and deployment of a Django project.

:Examples:

Execute tasks for the local server.

fab --config=config/local.conf local system.info

Execute tasks for the live server.

fab --config=config/live.conf live system.info
"""

from fabric.api import env, task, execute, settings

import postgres
import python
import system
import utils


env.user, env.password = env.SYSTEM_USER, env.SYSTEM_PASS

# Python packages to install.
env.python_packages = [
    'Django==1.8.4',
    'django-braces==1.8.0',
    'ipython==3.1.0',
    'psycopg2==2.6',
    'pytz==2015.2',
]

env.postgres_options = ' '.join([
    'NOCREATEROLE',
    'NOSUPERUSER',
    'NOINHERIT',
    'CREATEDB',
    'LOGIN',
])

env.postgres_version = '9.3'


@task
def live():
    """
    Initialize the "env" values for use in production environment.
    """
    env.hosts = [
        '192.168.10.10',
    ]
    
    env.environment = 'live'


@task
def local():
    """
    Initialize the "env" values for use in local environment.
    """
    env.hosts = [
        '192.168.10.10',
    ]
    
    env.environment = 'local'

    env.python_packages += [
        'django-debug-toolbar==1.3.0'
    ]


@task
def setup():
    """
    Setup a remote environment.

    :Example:
    
    fab --config=config/local.conf local setup
    """

    if env.environment == 'live':
        setup_live()
    else:
        setup_local()


def setup_live():
    pass


def setup_local():
    new_user = False

    # Ignore errors if the user already exists.
    with settings(user=env.ROOT_USER, password=env.ROOT_PASS, warn_only=True):
        # Create a new system user.
        result = execute('system.user_create', env.SYSTEM_USER, env.SYSTEM_PASS)

        if result.get(env.host):
            new_user = True

    # Upload SSH key if the new system user has been created.
    if new_user:
        execute('system.user_sshkey')

    execute('postgres.install')
    execute('postgres.config')

    # Ignore errors if the user already exists.
    with settings(warn_only=True):
        # Create a new postgres user.
        execute('postgres.user_create', env.POSTGRES_USER, env.POSTGRES_PASS)