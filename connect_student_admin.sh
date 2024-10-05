#! /bin/bash

PORT=22004
MACHINE=paffenroth-23.dyn.wpi.edu

ssh -i ~/CS553/Case_study_2/student-admin_key -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}
