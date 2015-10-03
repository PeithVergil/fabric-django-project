from fabric.api import cd, env, put, sudo, task
from fabric.contrib import files

import utils


@task
def install():
    """
    Install the PostgreSQL server.

    :Example:
    
    fab --config=config/local.conf local postgres.install
    """

    sudo('apt-get -y install libpq-dev postgresql postgresql-contrib')


@task
def restart():
    """
    Restart the PostgreSQL server.

    :Example:
    
    fab --config=config/local.conf local postgres.restart
    """

    sudo('service postgresql restart')


@task
def config():
    """
    Customize the configuration files of the PostgreSQL server.

    :Example:
    
    fab --config=config/local.conf local postgres.config
    """

    base_directory = '/etc/postgresql/{}/main'.format(env.postgres_version)

    conf_directory = '{}/conf.d'.format(base_directory)

    if not files.exists(conf_directory):
        # Create the "conf.d" directory.
        sudo('mkdir -p {}'.format(conf_directory))

        # Set directory permission to "744".
        sudo('chmod 744 {}'.format(conf_directory))

        # Set directory owner to "postgres".
        usr = grp = 'postgres'

        sudo('chown {}:{} {}'.format(usr, grp, conf_directory))

    if env.environment == 'live':
        config_live(base_directory, conf_directory)
    else:
        config_local(base_directory, conf_directory)


def config_live(base_directory, conf_directory):
    """
    Upload custom configuration files for live server.
    """


def config_local(base_directory, conf_directory):
    """
    Upload custom configuration files for local server.
    """

    local_path = utils.file_path('postgres/local.conf')

    remote_path = '{}/local.conf'.format(conf_directory)

    result = put(local_path, remote_path, mode=0644, use_sudo=True)

    if result.succeeded:
        pg_conf = '{}/postgresql.conf'.format(base_directory)

        files.append(pg_conf, "include_dir = 'conf.d'", use_sudo=True)

        # Set file owner to "postgres".
        usr = grp = 'postgres'

        sudo('chown {}:{} {}'.format(usr, grp, remote_path))
    
    # Grant access to remote clients.
    hba_conf = '{}/pg_hba.conf'.format(base_directory)

    files.append(hba_conf, 'host all all 0.0.0.0/0 md5', use_sudo=True)