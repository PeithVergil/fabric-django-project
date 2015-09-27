"""
Automate the setup of the local or live server.

:Examples:

Execute tasks for the local server.

fab --config=config/local.conf --roles=local local system.info

Execute tasks for the live server.

fab --config=config/live.conf --roles=live live system.info
"""

from fabric.api import env, task, execute, settings

import system
import utils


env.roledefs = {
    'live': [
        '192.168.10.10',
    ],
    'local': [
        '192.168.10.10',
    ],
}


@task
def live():
    """
    Initialize the "env" values for use in production environment.
    """
    env.environment = 'live'
    
    env.user, env.password = env.SYSTEM_USER, env.SYSTEM_PASS


@task
def local():
    """
    Initialize the "env" values for use in local environment.
    """
    env.environment = 'local'

    env.user, env.password = env.SYSTEM_USER, env.SYSTEM_PASS


@task
def setup():
    """
    Setup a remote environment.

    :Example:
    
    fab --config=config/local.conf --roles=local local setup
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