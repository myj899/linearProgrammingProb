# start from base
FROM python:3
LABEL maintainer="Julie Jung <myj899@gmail.com>"

# copy our application code
ADD ./ /

# fetch app specific deps
RUN pip install -r requirements.txt

# start app
CMD [ "python3", "./solverGUI.py" ]
