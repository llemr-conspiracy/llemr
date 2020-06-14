Translations
============

Translations will be placed in this folder when running::

    python manage.py makemessages

For defining the language which you want to translate you have to type following command with the language code. E.g. if you want to generate a german message file you have to type::

    python manage.py makemessages -l de


For making the translated strings of the `.po` file readable for django, you have to run following command to create the `.mo` binary file::
    python manage.py compilemessages
