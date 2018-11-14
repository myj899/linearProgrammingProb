# build the app container
docker build -t myj899/linprob .

# start the app container
docker run -d --name linprob myj899/linprob