from fabric.api import cd, env, run, task, sudo, prefix, require


@task
def build():
    """
    Install dependencies for building Python C extensions.

    :Example:
    
    fab --config=config/local.conf --roles=local local python.build_headers
    """
    
    # Python build headers.
    packages = [
        'python3-dev',
        'python3-tk',
    ]

    # Pillow build dependencies.
    packages += [
        'libfreetype6-dev',
        'libjpeg8-dev',
        'liblcms2-dev',
        'libtiff5-dev',
        'libwebp-dev',
        'tcl8.6-dev',
        'tk8.6-dev',
        'zlib1g-dev',
    ]

    sudo('apt-get -y install {}'.format(' '.join(packages)))


@task
def venv(name):
    """
    Create a new Python virtual environment.

    :param name: The name of the new virtual environment.

    :Example:
    
    fab --config=config/local.conf --roles=local local python.venv:name=myvenv
    """

    venvs_directory = '/home/{}/venvs'.format(env.user)

    # Put all virtual environments in one directory.
    run('mkdir -p {}'.format(venvs_directory))

    # In Ubuntu 14.04, there's an issue with Python 3's built-in pip.
    # So, virtual environments are created without pip.
    with cd(venvs_directory):
        run('python3 -m venv --without-pip {}'.format(name))

    # Activate the virtual environment then manually download and install pip.
    with prefix('source {}/{}/bin/activate'.format(venvs_directory, name)):
        run('curl https://bootstrap.pypa.io/get-pip.py | python')