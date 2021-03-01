#! /bin/bash
mysqldump -u root -h 10.69.68.42 -p root --all-databases > /home/quicklink/db/quicklinkbak.sql
sshpass -p root scp -r /home/quicklink/ root@10.69.81.232:/home/work/amy/quicklink/
echo "Backup Quicklink Done."
