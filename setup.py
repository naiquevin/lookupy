from distutils.core import setup

try:
    long_desc = open('./README.rst').read()
except IOError:
    long_desc = 'See: https://github.com/naiquevin/lookupy/blob/master/README.rst'

setup(
    name='Lookupy',
    version='0.1',
    author='Vineet Naik',
    author_email='naikvin@gmail.com',
    url='https://github.com/naiquevin/lookupy',
    packages=['lookupy',],
    license='MIT License',
    description='Django QuerySet inspired interface to query list of dicts',
    long_description=long_desc,
)

