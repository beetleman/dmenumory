from setuptools import setup

setup(
    name='Dmenumory',
    version='0.1',
    url='https://github.com/beetleman/dmenumory',
    description='Launcher build on top of dmenu  with simple launch statistic.',
    author='Mateusz Probachta aka beetleman',
    author_email='nigrantis.tigris@gmail.com',
    license="LGPL",
    keywords="dmenu launcher",
    long_description=open('README').read(),
    install_requires=['pyxdg'],
    packages=['dmenumory',
              'dmenumory.libs'],
    include_package_data=True,
    platforms='Linux',
    entry_points={"console_scripts": ["dmenumory=dmenumory.dmenumory:main"]},
)
