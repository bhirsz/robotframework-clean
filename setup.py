import pathlib
from setuptools import setup
from robocop.version import __version__


HERE = pathlib.Path(__file__).parent
README = (HERE / "README.rst").read_text()
CLASSIFIERS = """
License :: OSI Approved :: Apache Software License
Operating System :: OS Independent
Programming Language :: Python :: 3.6
Programming Language :: Python :: 3.7
Programming Language :: Python :: 3.8
Framework :: Robot Framework :: Tool
Topic :: Software Development :: Quality Assurance
Topic :: Utilities
""".strip().splitlines()

setup(
    name='robotframework-clean',
    version=__version__,
    description='Utility scripts for formatting Robot Framework code',
    long_description=README,
    long_description_content_type="text/x-rst",
    url="https://github.com/bhisz/robotframework-maid",
    author="Bartlomiej Hirsz",
    author_email="bartek.hirsz@gmail.com",
    license="Apache License 2.0",
    platforms="any",
    classifiers=CLASSIFIERS,
    packages=['robotclean'],
    include_package_data=True,
    install_requires=['robotframework>=3.2.1'],
    entry_points={'console_scripts': ['robotmaid=robotclean:run']}
)
