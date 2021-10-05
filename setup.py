import atexit

import pip
from setuptools import setup
from setuptools.command.install import install

# To install, run this command: python setup.py install
# If using virtualenv, make sure you're inside the desired environment.

pre_deps = [
]

post_deps = [
]


# _pre_install installs internal dependencies before the regular dependencies from the `install_requires` list
def _pre_install():
    for dep in pre_deps:
        pip.main(['install', '-I', dep, '--upgrade'])


# _post_install installs internal dependencies after the regular dependencies from the `install_requires` list
def _post_install():
    for dep in post_deps:
        pip.main(['install', '-I', dep, '--upgrade'])


# Custom dependency installation function
class Install(install):
    def __init__(self, *args, **kwargs):
        _pre_install()
        super(Install, self).__init__(*args, **kwargs)
        atexit.register(_post_install)


setup(
    name='referral_program_api',
    version='0.0.1',
    description='Referral Program API',
    author='Athus Vieira',
    author_email='athusvieira@gmail.com',
    url='',
    install_requires=[
        'psycopg2-binary==2.9.1',
        'sqlalchemy==1.4.20',
        'alembic==1.6.5',
        'marshmallow==3.9.1',
        'requests==2.25.0',
        'pycryptodome==3.10.1',
        'gunicorn==20.1.0',
        'flask==2.0.1',
        'pyjwt==1.7.1',
        'alchemy-mock==0.4.3',
        'faker==8.16.0'
    ],
    cmdclass={'install': Install}
)
