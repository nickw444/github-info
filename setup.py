from setuptools import setup

setup(
    name='github-info',
    version='0.0.1',
    description='Show GitHub information on Git pre-push or on demand',
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
