from setuptools import setup, find_packages


setup(
    name='rush_achievements_sdk',
    description='rush_achievements_sdk based on aiohttp',
    version='0.0.1',
    license='MIT',
    author="Petr Scherbakov",
    author_email='petrscherbakov93@gmail.com',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    url='https://github.com/petruxa77799/rush_achievements_sdk',
    keywords='rush_achievements_sdk based on aiohttp',
    install_requires=[
        'aiohttp',
    ],
)