Creating Backups and Copy to Host
======================================================================

Create Backups
----------------------------------------------------------------------

To create a backup of the postgres container, use the command:
    ::

        docker-compose -f production.yml (exec |run --rm) postgres backup

If you are on windows and the above command doesn't work, delete the headings in the script files you are calling, rebuild and run the server, and then use the command:
    ::

        docker exec -it llemr_postgres_1 /bin/bash usr/local/bin/backup

Note: If you want to view all of the backups you have created in the postgres container, replace backup with backups in the above commands


Copy to Host
----------------------------------------------------------------------

This command will copy the backups you have created to your local machine:
    ::

        docker cp llemr_postgres_1:./backups .
