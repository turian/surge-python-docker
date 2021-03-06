# surge-python-docker

Surge synthesizer through Python, dockerized

To build yourself:
```
docker build -t turian/surge-python-docker .
```

To run:
```
docker run -v output:/home/surge/output -it turian/surge-python-docker bash
```
