#! /bin/bash

PORT=22004
MACHINE=paffenroth-23.dyn.wpi.edu

ssh -i ../../scripts/student-admin_key -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}
