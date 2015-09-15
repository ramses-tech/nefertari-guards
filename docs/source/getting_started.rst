Getting started
===============

Add ``nefertari-guards`` to your requirements file or installing manually using:

.. code-block:: shell

    $ pip install nefertari-guards


Requirements
------------

* Python 2.7, 3.3 or 3.4
* Nefertari (or Ramses)


For Nefertari
-------------

1. add ``config.include('nefertari_guards')`` to your ``main()``
2. subclass your model classes with DocumentACLMixin
3. subclass your acl classes with DatabaseACLMixin

For Ramses
----------

- add ``database_acls = true`` to your .ini file
