from setuptools import setup
import os

def get_version():
    version_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'VERSION')
    v = open(version_path).read()
    if type(v) == str:
        return v.strip()
    return v.decode('UTF-8').strip()

readme_path = os.path.join(os.path.dirname(
    os.path.abspath(__file__)),
    'README.md',
)
long_description = open(readme_path).read()

try:
    version = get_version()
except Exception as e:
    version = '0.0.0-dev'


setup(
    name='github-info',
    version=version,
    description='Show GitHub information on Git pre-push or on demand',
    long_description=long_description,
    zip_safe=False,
    url='http://github.com/nickw444/github-info',
    author='Nick Whyte',
    author_email='nick@nickwhyte.com',
    license='MIT',
    scripts=['bin/github-info'],
    install_requires=[
        'colored==1.3.5',
        'requests==2.18.4'
    ]
)
