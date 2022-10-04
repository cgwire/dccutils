DCCUtils
=====================================

This library offers a serie of classes to abstract the most common features
available in Digital Content Creation (DCC) tools.

It currently supports Blender, Unreal, Maya and Houdini.

|Discord| |Downloads|

How to use it
-------------

Install the library:

.. code-block:: bash

    pip install dccutils


Then in your code (let's say you are working in Blender):

.. code-block:: python

    from dccutils import BlenderContext

    dcc_software_manager.blender = BlenderContext()
    print(dcc_software_manager.get_cameras())


Contributions
-------------

All contributions are welcome as long as they respect the `C4
contract <https://rfc.zeromq.org/spec:42/C4>`__.

Code must follow the pep8 convention.

You can use the pre-commit hook for Black (a python code formatter) before commiting :

.. code:: bash

    pip install pre-commit
    pre-commit install


About authors
-------------

DCCUtils is written by CGWire, a company based in France. We help animation and VFX studios to collaborate better through efficient tooling. We already work with more than 70 studios around the world.

Visit `cg-wire.com <https://cg-wire.com>`__ for more information.

|CGWire Logo|

.. |Discord| image:: https://badgen.net/badge/icon/discord?icon=discord&label
   :target: https://discord.com/invite/VbCxtKN
.. |CGWire Logo| image:: https://zou.cg-wire.com/cgwire.png
   :target: https://cg-wire.com
.. |Downloads| image:: https://static.pepy.tech/personalized-badge/dccutils?period=month&units=international_system&left_color=grey&right_color=orange&left_text=Downloads
   :target: https://pepy.tech/project/dccutils
