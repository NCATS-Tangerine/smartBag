# install python
FROM python:3.6.5

# make a dir for the git repo
#RUN mkdir ./repo

# go there
#WORKDIR repo

# get the smartBag repo
RUN git clone http://github.com/NCATS-Tangerine/smartBag.git

# install the needed packages
RUN pip install -r ./smartBag/requirements.txt

# update
RUN apt-get update

EXPOSE 5000

# change to the directory with the web site smart via the smartbag script
WORKDIR /smartBag

ENTRYPOINT ["/bin/bash", "-c", "./smartbag run smartapi --port 5000"]
