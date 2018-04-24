import os
import sys

from setuptools import find_packages, setup
from setuptools.command.test import test as TestCommand

PACKAGE_TYPE = 'ivangirko'
PACKAGE_NAME = 'trader'
PACKAGE_DESC = 'Stock bot trader'
PACKAGE_LONG_DESC = 'Currently trade on Binance'
PACKAGE_VERSION = '0.1.0'


class PyTest(TestCommand):

    user_options = [('pytest-args=', 'a', "Arguments to pass to pytest")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        # default list of options for testing
        # https://docs.pytest.org/en/latest/logging.html
        self.pytest_args = (
            '--flake8 {0} tests examples ' \
            '--junitxml=.reports/{0}_junit.xml ' \
            '--cov={0} --cov=tests ' \
            '-p no:logging'.format(PACKAGE_NAME.replace('-', '_'))
        )

    def run_tests(self):
        import shlex
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(shlex.split(self.pytest_args))
        sys.exit(errno)


# Что нужно для запуска python setup.py <any_cmd>
# Используем ручной запуск с помощью класса PyTest
setup_requires = []


# Что нужно для установки
install_requires = [
    'pyyaml>=3.12',
    'aiohttp>=3.1.3',
]


# Что нужно для запуска python setup.py test
tests_require = [
    'pytest',
    'pytest-cov',
    'pytest-flake8',
    'pytest-asyncio',
    'pytest-sugar',
    'asynctest',
]


# Скрипты
console_scripts = [
    'trade=trader.main:main'
]


setup(
    name=PACKAGE_NAME,
    version=PACKAGE_VERSION,
    description=PACKAGE_DESC,
    long_description=PACKAGE_LONG_DESC,
    url='https://github.com/{}/{}'.format(PACKAGE_TYPE, PACKAGE_NAME),
    author="Ivan Girko",
    author_email="energyclab90@gmail.com",
    license="Nodefined",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Framework :: AsyncIO',
        'Framework :: Aiohttp',
        'Framework :: Pytest',
        'Intended Audience :: Customer Service',
        'Intended Audience :: Information Technology',
        'License :: Other/Proprietary License',
        'Natural Language :: Russian',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    zip_safe=False,
    packages=find_packages(exclude=['tests', 'examples', '.reports']),
    entry_points={'console_scripts': console_scripts},
    python_requires='>=3.5',
    setup_requires=setup_requires,
    install_requires=install_requires,
    tests_require=tests_require,
    cmdclass={'test': PyTest},
)
