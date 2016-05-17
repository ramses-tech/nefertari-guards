import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))
README = open(os.path.join(here, 'README.md')).read()
VERSION = open(os.path.join(here, 'VERSION')).read()

requires = [
    'nefertari>=0.7.0',
    'pyramid',
    'sqlalchemy_utils',
]

setup(
    name='nefertari-guards',
    version=VERSION,
    description='Advanced ACLs for Nefertari',
    long_description=README,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author='Ramses',
    author_email='hello@ramses.tech',
    url='https://github.com/ramses-tech/nefertari-guards',
    keywords='web pyramid pylons nefertari acl',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=requires,
    tests_require=requires,
    test_suite="nefertari_guards",
    entry_points="""\
    [console_scripts]
        nefertari-guards.count_ace = nefertari_guards.scripts.count_ace:main
        nefertari-guards.update_ace = nefertari_guards.scripts.update_ace:main
    """,
)
