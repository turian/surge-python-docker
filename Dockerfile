FROM ubuntu:18.04
ENV LANG C.UTF-8
LABEL maintainer="lastname@gmail.com"
LABEL version="0.1"
LABEL description="Surge synthesizer through Python, dockerized"

WORKDIR /root/

ENV TZ=Etc/UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Disable Prompt During Packages Installation
ARG DEBIAN_FRONTEND=noninteractive

# Update Ubuntu Software repository
RUN apt-get update
RUN apt-get upgrade -y

# Build tools
RUN apt-get install -y git build-essential python3-pip
RUN apt-get install -y libcairo-dev libxkbcommon-x11-dev libxkbcommon-dev libxcb-cursor-dev libxcb-keysyms1-dev libxcb-util-dev
RUN apt-get install -y vim rsync
RUN apt-get install -y libsndfile-dev vorbis-tools

RUN apt-get remove cmake -y
RUN apt-get install -y apt-transport-https ca-certificates gnupg software-properties-common wget  libssl1.0-dev 
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | apt-key add -
RUN apt-add-repository 'deb https://apt.kitware.com/ubuntu/ bionic main' > /dev/null
RUN apt-get update
RUN apt-get install cmake -y

# Some command line utils you probably want
#RUN apt-get install -y sudo less bc screen tmux unzip vim wget

# Add non root user
RUN useradd -ms /bin/bash surge && echo "surge:surge" | chpasswd && adduser surge sudo
USER surge
ENV HOME /home/surge

# Clone surge from master, and build
#RUN cd ~ && git clone https://github.com/surge-synthesizer/surge.git
#RUN cd ~ && git clone --depth 1 --branch release/1.8.1 https://github.com/surge-synthesizer/surge.git
RUN cd ~ && wget https://github.com/surge-synthesizer/releases/releases/download/1.8.1/SurgeSrc_1.8.1.tgz && tar zxvf SurgeSrc_1.8.1.tgz && rm SurgeSrc_1.8.1.tgz
#RUN cd ~/surge/ && git submodule update --init --recursive
RUN cd ~/surge/ && /usr/bin/cmake -Bbuildpy -DBUILD_SURGE_PYTHON_BINDINGS=TRUE -DCMAKE_BUILD_TYPE=Release

RUN cd ~/surge/ && LD_LIBRARY_PATH="/usr/lib/python3.6/config-3.6m-x86_64-linux-gnu/:$LD_LIBRARY_PATH" /usr/bin/cmake --build buildpy --config Release --target surgepy

USER surge
COPY example.py /home/surge/example.py
COPY run.py /home/surge/run.py

RUN cd ~/surge/ && ./build-linux.sh build --local --project=headless
RUN mkdir -p /home/surge/.local/share/surge
RUN cd ~/surge/ && ./build-linux.sh install --local --project=headless
RUN mv ~/surge/buildpy/surgepy.cpython-36m-x86_64-linux-gnu.so ~
RUN rm -Rf ~/surge
RUN echo "PYTHONPATH=\"$PYTHONPATH:/home/surge\"" >> ~/.bashrc

USER root
# Some of these packages are not totally necessary, but useful nonetheless
RUN pip3 install --upgrade tqdm ipython numpy soundfile python-slugify
# remove unused files
RUN apt-get remove -y libcairo-dev libxkbcommon-x11-dev libxkbcommon-dev libxcb-cursor-dev libxcb-keysyms1-dev libxcb-util-dev
RUN apt-get remove -y git build-essential cmake
RUN apt-get autoclean && apt-get autoremove -y && rm -rf /var/lib/apt/lists/*

USER surge
