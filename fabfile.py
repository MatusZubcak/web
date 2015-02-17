from fabric.api import run, cd, prefix, env
import os

PROJECT_PATH = '~/web'
LOCAL = False
DEFAULT_VIRTUALENV_NAME = 'trojstenweb'
VIRTUALENV_NAME = 'trojstenweb'

def _reset_env():
    global PROJECT_PATH
    global LOCAL
    global VIRTUALENV_NAME
    LOCAL = False
    PROJECT_PATH = '~/web'
    VIRTUALENV_NAME = DEFAULT_VIRTUALENV_NAME

def beta():
    _reset_env()
    env.user = 'betakspweb'
    env.hosts = ['archiv.ksp.sk']

def prod():
    _reset_env()
    env.user = 'trojstenweb'
    env.hosts = ['archiv.ksp.sk']

def local(venvname=DEFAULT_VIRTUALENV_NAME):
    global PROJECT_PATH
    global LOCAL
    global VIRTUALENV_NAME
    env.user = os.environ.get('USER')
    env.hosts = ['localhost']
    PROJECT_PATH = os.path.dirname(os.path.realpath(__file__))
    LOCAL = True
    VIRTUALENV_NAME = venvname

def pull():
    with cd(PROJECT_PATH):
        run('git pull')

def collectstatic():
    manage('collectstatic', '--noinput')

def syncdb():
    manage('syncdb', '--noinput')

def migrate():
    manage('migrate', '--noinput')

def load_fixtures():
    manage('loaddata', 'fixtures/*')

def install_requirements():
    with cd(PROJECT_PATH):
        with prefix('workon %s' % VIRTUALENV_NAME):
            run('pip install -r requirements.txt')
            if LOCAL:
                run('pip install -r requirements.devel.txt')

def manage(*args):
    with cd(PROJECT_PATH):
        with prefix('workon %s' % VIRTUALENV_NAME):
            run('python manage.py ' + ' '.join(args))

def restart_wsgi():
    with cd(PROJECT_PATH):
        run('touch trojsten/*.wsgi')

def write_version_txt():
    with cd(PROJECT_PATH):
        run('git log --no-merges --pretty=format:"%h %cd" -n 1 --date=short > version.txt')
        run('echo >> version.txt')

def enable_maintenance_mode():
    run('touch ~/maintenance')

def disable_maintenance_mode():
    run('rm -f ~/maintenance')

def update():
    if not LOCAL:
        enable_maintenance_mode()
    pull()
    install_requirements()
    syncdb()
    migrate()
    if not LOCAL:
        collectstatic()
        restart_wsgi()
        disable_maintenance_mode()
    write_version_txt()

def version():
    with cd(PROJECT_PATH):
        run('cat version.txt')
