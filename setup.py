from setuptools import find_packages, setup

setup(
    name='brpc',
    version='v5.0.0',
    package_dir={"": "src"},
    packages=find_packages(exclude=["tests", "test.*"]),
    install_requires=[
        'prometheus-client==0.13.1', 'pyyaml==6.0', 'schema==0.7.5',
        'websockets==10.4', 'structlog==22.1.0', 'requests==2.28.1',
        'jsonrpcclient==4.0.2'
    ],
    extras_require={
        'test': [
            'pylint>=2.15.8', 'pep8>=1.7.1', 'pytest>=7.2.0',
            'pytest-asyncio>=0.20.3', 'requests-mock>=1.10.0',
            'pytest-cov>=4.0.0', 'yapf>=0.32.0'
        ]
    },
    entry_points='''
        [console_scripts]
        brpc=exporter:main
    ''',
)
