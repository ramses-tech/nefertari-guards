ACL Filtering
=============

ACL filtering is one of the features of nefertari-guards. The main idea of ACL filtering is - when requesting collection (GET/PATCH/DELETE), corresponding permissions of each item are checked and if user doesn't have permission to access the item, it is dropped from resulting response.

How It Works
------------

User is considered to be allowed to see collection item in results if:
    1. Any of his principals are ``Allow``'ed either ``all`` or current request permission; AND
    2. None of his principals are ``Deny``'ed either ``all`` or current request permission.

Pemissions checked:
    * collection GET: ``all``, ``view``
    * collection PATCH: ``all``, ``update``
    * collection DELETE: ``all``, ``delete``

Things to consider when working with ACL filtering:
    1. ACEs that ``Deny`` supersede ACEs that ``Allow``.
    2. The items that a user gets on collection GET does not necessarly guarantee that all of those items will affected by collection PATCH or DELETE. E.g. if item allows ``view`` to user but doesn't allow ``update``, that item will be visible to user on collection GET, but won't be affected by collection PATCH.
    3. ACL filtering does not take into account (does not inherit) collection ACL.

Examples
--------

Let's consider a user that performs a collection GET request ('view' permission) and has the following principal identifiers: "john", "group1", "everyone", "authenticated".

**Items with the following ACLs will be visible to that user:**

User 'john' is explicitly allowed to view an item (and not denied):

.. code-block:: python

    [(Allow, 'john', 'view')]
    # OR
    [(Allow, 'john', ALL_PERMISSIONS)]

User's group is explicitly allowed to view an item (and not denied):

.. code-block:: python

    [(Allow, 'group1', 'view')]
    # OR
    [(Allow, 'group1', ALL_PERMISSIONS)]

Everyone is explicitly allowed to view an item (and not denied):

.. code-block:: python

    [(Allow, Everyone, 'view')]
    # OR
    [(Allow, Everyone, ALL_PERMISSIONS)]

Authenticated is explicitly allowed to view an item (and not denied):

.. code-block:: python

    [(Allow, Authenticated, 'view')]
    # OR
    [(Allow, Authenticated, ALL_PERMISSIONS)]

User 'john' is explicitly allowed to view an item and access is denied to users of 'group2' to which user does NOT belong:

.. code-block:: python

    [
        (Allow, 'john', 'view'),
        (Deny, 'group2', 'view'),
    ]

User 'john' is explicitly allowed to view an item and access is denied to user 'john' to update:

.. code-block:: python

    [
        (Allow, 'john', 'view'),
        (Deny, 'john', 'update'),
    ]

**Items with following ACLs will NOT be visible to that user:**

User 'john' is explicitly denied to view an item:

.. code-block:: python

    [(Deny, 'john', 'view')]
    # OR
    [(Deny, 'john', ALL_PERMISSIONS)]

Everyone or Authenticated users are denied to view the item (user is Everyone and is Authenticated):

.. code-block:: python

    [(Deny, Everyone, 'view')]
    # OR
    [(Deny, Authenticated, 'view')]
    # OR
    [(Deny, Everyone, ALL_PERMISSIONS)]
    # OR
    [(Deny, Authenticated, ALL_PERMISSIONS)]

User 'john' is explicitly allowed to see an item BUT access is denied to 'group1' to which user belongs (order of ACEs doesn't matter):

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
