#! /bin/bash

SSH_KEY=~/CS553/Case_study_2/student-admin_key
PORT=22004
MACHINE=paffenroth-23.dyn.wpi.edu

ssh -i ${SSH_KEY} -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}

