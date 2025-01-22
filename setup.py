from setuptools import setup, find_packages

setup(
    name='drawing_task',
    version='1.0.0',
    packages=find_packages(),
    install_requires=[
        'PyQt5',
        'requests'
    ],
    entry_points={
        'console_scripts': [
            'drawing_task=main:main',
        ],
    },
    include_package_data=True,
)
