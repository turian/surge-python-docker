# surge-python-docker

Surge synthesizer through Python, dockerized

To build yourself:
```
docker build -t turian/surge-python-docker .
```

To run:
```
docker run --rm --mount source=`pwd`/output,target=/home/surge/output,type=bind -it turian/surge-python-docker bash
```
