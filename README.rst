DCC Utils
---------

This library offers a series of classes to abstract the most common features 
available in Digital Content Creation tools.

It currently supports Blender, Maya and Houdini.


How to use it
-------------

Install the library:

```
pip install dccutils
```

Then in your code (let's say you are working in blender):

.. code-block:: python
    from dccutils import BlenderContext

    dcc_software_manager = BlenderContex()
    dcc_software_manager.list_cameras()


Contributions
-------------

All contributions are welcome as long as they respect the `C4
contract <https://rfc.zeromq.org/spec:42/C4>`__.

Code must follow the pep8 convention.


About authors
-------------

Gazu is written by CG Wire, a company based in France. We help indie creative 
studios to pipeline and workflow efficiently.

We apply software craftmanship principles as much as possible. We love
coding and consider that strong quality and good developer experience
matter a lot. Our extensive knowledge allows studios to get better at
managing production and doing software. They can focus more on the artistic
work.

Visit `cg-wire.com <https://cg-wire.com>`__ for more information.

|CGWire Logo|

.. |Build status| image:: https://api.travis-ci.org/cgwire/gazu.svg?branch=master
   :target: https://travis-ci.org/cgwire/gazu
.. |CGWire Logo| image:: https://zou.cg-wire.com/cgwire.png
   :target: https://cg-wire.com
