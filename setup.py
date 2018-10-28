from distutils.core import setup

try:
    long_desc = open('./README.rst').read()
except IOError:
    long_desc = 'See: https://github.com/naiquevin/lookupy/blob/master/README.rst'

setup(
    name='lookupy-unmanaged',
    version='0.1',
    author='Vineet Naik',
    author_email='naikvin@gmail.com',
    url='https://github.com/jpic/lookupy',
    packages=['lookupy',],
    license='MIT License',
    description='Temp. package to release model support in lookupy',
    long_description=long_desc,
)
