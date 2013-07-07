from distutils.core import setup

setup(
    name='Lookupy',
    version='0.1',
    author='Vineet Naik',
    author_email='naikvin@gmail.com',
    packages=['lookupy',],
    license='MIT License',
    description='Django QuerySet inspired interface to query list of dicts',
    long_description=open('README.md').read(),
)

