Translations
============

Translations will be placed in this folder when running::

    python manage.py makemessages

For defining the language which you want to translate you have to type following command with the language code. E.g. if you want to generate a german message file you have to type::

    python manage.py makemessages -l de


After the message file has been created it has to be compiled to a more efficient form. This also applies if changes has been made to a message file. Run this command::

    python manage.py compilemessages
