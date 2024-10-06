#! /bin/bash

PORT=22004
MACHINE=paffenroth-23.dyn.wpi.edu
STUDENT_ADMIN_KEY_PATH=~/CS553/Case_study_2

# Clean up from previous runs
ssh-keygen -f "/home/jgeoghegan/.ssh/known_hosts" -R "[paffenroth-23.dyn.wpi.edu]:22004"
rm -rf tmp

# Create a temporary directory
mkdir tmp

# copy the key to the temporary directory
cp ${STUDENT_ADMIN_KEY_PATH}/student-admin_key* tmp

# Change to the temporary directory
cd tmp

# Set the permissions of the key
chmod 600 student-admin_key*

# Prompt the user for a passphrase
read -sp "Enter a passphrase for the new key: " PASSPHRASE
echo

# Create a unique key with the user-provided passphrase
rm -f mykey*
ssh-keygen -f mykey -t ed25519 -N "$PASSPHRASE"

# Remove the default student-admin key
ssh -i student-admin_key -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE} "sed -i '/rcpaffenroth@paffenroth-23/d' ~/.ssh/authorized_keys"

# Insert the key into the authorized_keys file on the server
# One > creates
cat mykey.pub > authorized_keys
# two >> appends
# Remove to lock down machine
#cat student-admin_key.pub >> authorized_keys

chmod 600 authorized_keys

echo "checking that the authorized_keys file is correct"
ls -l authorized_keys
cat authorized_keys

# Copy the authorized_keys file to the server
scp -i student-admin_key -P ${PORT} -o StrictHostKeyChecking=no authorized_keys student-admin@${MACHINE}:~/.ssh/

# Add the key to the ssh-agent
eval "$(ssh-agent -s)"
ssh-add mykey

# Check the key file on the server
echo "checking that the authorized_keys file is correct"
ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE} "cat ~/.ssh/authorized_keys"

# clone the repo
git clone https://github.com/adequatej/CS553_casestudy1

# Copy the files to the server
scp -P ${PORT} -o StrictHostKeyChecking=no -r CS553_casestudy1 student-admin@${MACHINE}:~/

# check that the code is installed and start up the product
# COMMAND="ssh -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}"

# ${COMMAND} "ls ~/CS553_casestudy1"
# ${COMMAND} "sudo apt install -qq -y python3-venv"
# ${COMMAND} "cd ~/CS553_casestudy1 && python3 -m venv venv"
# ${COMMAND} "cd ~/CS553_casestudy1 && source venv/bin/activate && pip install -r requirements.txt"
# ${COMMAND} "nohup ~/CS553_casestudy1/venv/bin/python3 ~/CS553_casestudy1/app.py > log.txt 2>&1 &"

# nohup ./whatever > /dev/null 2>&1 

# debugging ideas
# sudo apt-get install gh
# gh auth login
# requests.exceptions.HTTPError: 429 Client Error: Too Many Requests for url: https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta/v1/chat/completions
# log.txt
