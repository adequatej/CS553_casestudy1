#! /bin/bash

PORT=22004
MACHINE=paffenroth-23.dyn.wpi.edu

# Change to the temporary directory
cd tmp

# Add the key to the ssh-agent
echo "Starting SSH agent and adding key"
eval "$(ssh-agent -s)"
# with error handling
ssh-add mykey || { echo "[ERROR] Failed to add SSH key"; exit 1; }

# check that the code in installed and start up the product

COMMAND="ssh -i mykey -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}"

echo "Checking project directory and setting up virtual environment"

${COMMAND} "ls ~/CS553_casestudy1"
${COMMAND} "sudo apt install -qq -y python3-venv"
${COMMAND} "cd ~/CS553_casestudy1 && python3 -m venv venv"
${COMMAND} "cd ~/CS553_casestudy1 && source venv/bin/activate && pip install -r requirements.txt"
${COMMAND} "nohup ~/CS553_casestudy1/venv/bin/python3 ~/CS553_casestudy1/app.py > log.txt 2>&1 &"
