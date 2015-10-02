from fabric.api import env, run, task, sudo, require
from fabric.contrib import files

import utils


@task
def info():
    """
    Get some details about the remote system.

    :Example:
    
    fab --config=config/local.conf local system.info
    """

    run('uname -a')


@task
def update():
    """
    Update the system packages.

    :Example:
    
    fab --config=config/local.conf local system.update
    """

    sudo('apt-get -y update')
    sudo('apt-get -y upgrade')


@task
def autoremove():
    """
    Remove unused system packages.

    :Example:
    
    fab --config=config/local.conf local system.autoremove
    """

    sudo('apt-get -y autoremove')


@task
def user_create(username, password):
    """
    Create a new system user with sudo privileges.

    :param username: The new username.
    :param password: The raw password.

    :Example:
    
    fab --config=config/local.conf local system.user_create:username=hello,password=world
    """

    result = add_usr(username)

    if result.succeeded:
        add_grp(username, 'sudo')

    if result.succeeded:
        set_pwd(username, password)

    return result.succeeded


@task
def user_delete(username):
    """
    Delete an existing system user.

    :param username: The user to delete.

    :Example:
    
    fab --config=config/local.conf local system.user_delete:username=hello
    """

    sudo('deluser {}'.format(username))


@task
def user_sshkey():
    """
    Upload an SSH key to the remote system for the current user.

    :Example:
    
    fab --config=config/local.conf local system.user_sshkey
    """

    require('PUBLIC_SSH_KEY')

    with open(env.PUBLIC_SSH_KEY) as reader:
        key = reader.read()

    remote_directory = '/home/{}/.ssh'.format(env.user)
    
    remote_authkeys = '{}/authorized_keys'.format(remote_directory)

    new_directory = False
    
    if not files.exists(remote_directory):
        new_directory = True
        
        # Create the ".ssh" directory.
        run('mkdir -p {}'.format(remote_directory))
    
    # Add the key to "authorized keys".
    files.append(remote_authkeys, key)

    if new_directory:
        # Set directory permission to "700".
        run('chmod 700 {}'.format(remote_directory))

        # Set file permission to "600".
        run('chmod 600 {}'.format(remote_authkeys))


def add_usr(username):
    """
    Create a new system user with no password.
    """
    return sudo('adduser --disabled-password --gecos "" {}'.format(username))


def add_grp(username, group):
    """
    Add an existing user to a group.
    """
    return sudo('adduser {} {}'.format(username, group))


def set_pwd(username, password):
    """
    Set a password to an existing user.
    """

    # Hash the raw password.
    password = utils.hash(password)

    return sudo("echo '{}:{}' | chpasswd -e".format(username, password))