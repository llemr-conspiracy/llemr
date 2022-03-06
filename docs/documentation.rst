Project Documentation
======================================================================

Get Started
----------------------------------------------------------------------

`Sphinx <https://www.sphinx-doc.org/>`_ is the tool used to build documentation.

Documentation can be written as rst files in the `osler/docs/_source`.

To build and serve docs, use the commands:
    ::
    
        docker-compose -f docs.yml build
        docker-compose -f docs.yml up

Changes to files in `docs/_source` will be picked up and reloaded automatically.

Docstrings to Documentation
----------------------------------------------------------------------

.. warning::
	This functionality is not currently working. It is here for reference in the future only.

The sphinx extension `apidoc <https://www.sphinx-doc.org/en/master/man/sphinx-apidoc.html/>`_ is used to automatically document code using signatures and docstrings.

Numpy or Google style docstrings will be picked up from project files and availble for documentation. See the `Napoleon <https://sphinxcontrib-napoleon.readthedocs.io/en/latest/>`_ extension for details.

For an in-use example, see `django-cookiecutter's` `users.rst.txt` documentation.

To compile all docstrings automatically into documentation source files, use the command:
    ::
    
        make apidocs

This can be done in the docker container:
    :: 
        
        docker run --rm docs make apidocs
