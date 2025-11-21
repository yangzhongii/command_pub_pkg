from setuptools import setup, find_packages
import os
from glob import glob

package_name = 'command_pub_pkg'

setup(
    name=package_name,
    version='0.0.1',
    # packages=[package_name],
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),

        (os.path.join('share', package_name, 'launch'), glob('launch/*.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='yangzhongii',
    maintainer_email='zhy26399@outlook.com',
    description='voice command publish',
    license='Apache-2.0',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            
            'command_pub = command_pub_pkg.command_pub:main'
        ],
    },
)