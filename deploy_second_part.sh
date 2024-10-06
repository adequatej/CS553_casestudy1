#! /bin/bash

PORT=22004
MACHINE=paffenroth-23.dyn.wpi.edu

# Change to the temporary directory
cd tmp

# Add the key to the ssh-agent
eval "$(ssh-agent -s)"
ssh-add mykey

# check that the code in installed and start up the product
COMMAND="ssh -i tmp/mykey -p ${PORT} -o StrictHostKeyChecking=no student-admin@${MACHINE}"
${COMMAND} "ls ~/CS553/Case_study_1/Chatbot2"
${COMMAND} "sudo apt install -qq -y python3-venv"
${COMMAND} "cd ~/CS553/Case_study_1/Chatbot2 && python3 -m venv venv"
${COMMAND} "cd ~/CS553/Case_study_1/Chatbot2 && source venv/bin/activate && pip install -r requirements.txt"
${COMMAND} "nohup ~/CS553/Case_study_1/Chatbot2/venv/bin/python3 ~/CS553/Case_study_1/Chatbot2/app.py > log.txt 2>&1 &"

# nohup ./whatever > /dev/null 2>&1 

# debugging ideas
# sudo apt-get install gh
# gh auth login
# requests.exceptions.HTTPError: 429 Client Error: Too Many Requests for url: https://api-inference.huggingface.co/models/HuggingFaceH4/zephyr-7b-beta/v1/chat/completions
# log.txt
