ACL Filtering
=============

ACL filtering is one of the features of nefertari-guards.
The main idea of ACL filtering is - when requesting collection (GET/PATCH/DELETE), corresponding permissions of each item are checked and if user doesn't have permission to access the item, it is dropped from resulting response.

How it works
------------

User is considered to be allowed to see collection item in results if:
1. Any of his principals are ``Allow``'ed any permissions: ``all`` or current request permission
AND
2. None of his principals are ``Deny``'ed any of permissions: ``all`` or current request permission

Also note that ACEs  that ``Deny`` access supersede ACEs that ``Allow`` access.

Pemissions checked:
    * collection GET: ``all``, ``view``
    * collection PATCH: ``all``, ``update``
    * collection DELETE: ``all``, ``delete``

Things to consider when working with ACL filtering:
    1. If users sees particular items on collection GET it's guaranteed all of those items will affected by collection PATCH/DELETE. E.g. if item allows ``view`` to user but doesn't allow ``update``, that item will be visible to user on collection GET, but won't be affected by collection PATCH, as it will be filtered out.
    2. ACL filtering does not take into account (does not inherit) collection ACL.

Examples
--------

Having user that performs collection GET request('view' permission) and has principal identifiers: "john", "group1", "everyone", "authenticated".

**Items with following ACLs will be visible to user:**

User 'john' is explicitly allowed to see an item and not denied:

.. code-block:: python

    [(Allow, 'john', 'view')]
    # OR
    [(Allow, 'john', ALL_PERMISSIONS)]

User's group is explicitly allowed to see an item and not denied:

.. code-block:: python

    [(Allow, 'group1', 'view')]
    # OR
    [(Allow, 'group1', ALL_PERMISSIONS)]

Everyone is explicitly allowed to see an item and not denied:

.. code-block:: python

    [(Allow, Everyone, 'view')]
    # OR
    [(Allow, Everyone, ALL_PERMISSIONS)]

Authenticated is explicitly allowed to see an item and not denied:

.. code-block:: python

    [(Allow, Authenticated, 'view')]
    # OR
    [(Allow, Authenticated, ALL_PERMISSIONS)]

User 'john' is explicitly allowed to see an item and access is denied to users of 'group2' to which user does NOT belong:

.. code-block:: python

    [
        (Allow, 'john', 'view'),
        (Deny, 'group2', 'view'),
    ]

User 'john' is explicitly allowed to see an item and access is denied to user 'john' to update item:

.. code-block:: python

    [
        (Allow, 'john', 'view'),
        (Deny, 'john', 'update'),
    ]

**Items with following ACLs will NOT be visible to user:**

User 'john' is explicitly denied to see an item:

.. code-block:: python

    [(Deny, 'john', 'view')]
    # OR
    [(Deny, 'john', ALL_PERMISSIONS)]

Everyone or Authenticated are denied to see the item and user has those principal identifiers (user is Everyone and user is Authenticated):

.. code-block:: python

    [(Deny, Everyone, 'view')]
    # OR
    [(Deny, Authenticated, 'view')]
    # OR
    [(Deny, Everyone, ALL_PERMISSIONS)]
    # OR
    [(Deny, Authenticated, ALL_PERMISSIONS)]

User 'john' is explicitly allowed to see an item BUT access is denied to 'group1' to which user belongs(note that order of ACEs doesn't matter):

.. code-block:: python

    [
        (Allow, 'john', 'view'),
        (Deny, 'group1', 'view'),
    ]
    # OR
    [
        (Deny, 'group1', 'view'),
        (Allow, 'john', 'view'),
    ]
