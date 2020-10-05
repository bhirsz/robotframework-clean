Robot Clean
===============

.. contents::
   :local:

Introduction
------------

Requirements
------------

Python 3.6+ and Robot Framework 3.2.1+.

Installation
------------

You can install RobotClean simply by running::

    pip install robotframework-clean


Usage
-----
RobotClean support following modes (you can mix them):

splitting keyword(s)
~~~~~~~~~~~~~~~~~~~~

    robotclean  --mode split  --path test.robot --line 10  --end-line 10


It will split keyword(s) at given location. Example::

    Keyword  ${var}  ${var2}

to::

    Keyword
    ...    ${var}
    ...    ${var2}

renaming keyword(s)
~~~~~~~~~~~~~~~~~~~

    robotclean  --mode rename  --path test.robot

It will rename keyword(s) at given location to follow Title Case. Example::

    this_is_keyword
    This Is Keyword
    This is keyword
    And also ABBREV

to::

   This Is Keyword
   This Is Keyword
   This Is Keyword
   And Also ABBREV

aligning to column(s)
~~~~~~~~~~~~~~~~~~~~~

    robotclean  --mode align  --path test.robot --line 5  --end-line 10

It will align variables and keywords to column like appearance. Example::

    ${var}  Keyword  ${var1}  4  test  ${var}  test=${5}
    Longer Keyword  ${var}
    ${value}  Set Variable If  ${value}==True  5

to::

    ${var}              Keyword             ${var1}             4       test    ${var}      test=${5}
    Longer Keyword      ${var}
    ${value}            Set Variable If     ${value}==True      5

replacing tabs to spaces
~~~~~~~~~~~~~~~~~~~~~~~~

    robotclean  --mode tabs_to_spaces  --path test.robot

It will replace all tab character by spaces (while trying to preserve aligment)

adjusting whitespace
~~~~~~~~~~~~~~~~~~~~

    robotclean  --mode whitespace  --path test.robot

It will adjust whole robot file to set of rules:
- no empty sections allowed
- 2 empty lines between sections
- 1 empty line between tests and keywords
- 1 trailing line at the end of file
- no trailing whitespace
