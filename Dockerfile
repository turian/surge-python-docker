# Use Ubuntu 22.04 LTS base image
FROM ubuntu:22.04

# Set environment variables
ENV LANG C.UTF-8
ENV TZ=Etc/UTC
ENV DEBIAN_FRONTEND=noninteractive

# Metadata
LABEL maintainer="lastname@gmail.com"
LABEL version="0.2"
LABEL description="Surge synthesizer through Python, dockerized on Ubuntu 22.04 LTS"

# Set working directory
WORKDIR /root/

# Set timezone
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Update and upgrade Ubuntu packages
RUN apt-get update && \
    apt-get upgrade -y && \
    apt-get install -y \
    git \
    build-essential \
    python3-pip \
    libcairo2-dev \
    libxkbcommon-x11-0 \
    libxkbcommon-dev \
    libxcb-cursor-dev \
    libxcb-keysyms1-dev \
    libxcb-util-dev \
    vim \
    rsync \
    less \
    bc \
    libsndfile-dev \
    vorbis-tools \
    apt-transport-https \
    ca-certificates \
    gnupg \
    software-properties-common \
    wget \
    libssl-dev

# Install updated CMake from Kitware
RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor -o /usr/share/keyrings/kitware-archive-keyring.gpg && \
    echo 'deb [signed-by=/usr/share/keyrings/kitware-archive-keyring.gpg] https://apt.kitware.com/ubuntu/ jammy main' | tee /etc/apt/sources.list.d/kitware.list >/dev/null && \
    apt-get update && \
    apt-get install cmake -y

# Add non-root user
RUN useradd -ms /bin/bash surge && echo "surge:surge" | chpasswd && adduser surge sudo

# Switch to non-root user
USER surge
ENV HOME /home/surge

# Clone the specific tag of Surge Synthesizer
RUN cd ~ && git clone --branch release_xt_1.2.3 --depth 1 https://github.com/surge-synthesizer/surge.git
RUN cd ~/surge/ && git submodule update --init --recursive

USER root

# Install necessary dependencies for Surge synthesizer
RUN apt-get install -y \
    libxrandr-dev \
    libasound2-dev \
    libcurl4-openssl-dev \
    libwebkit2gtk-4.0-dev \
    libgtk-3-dev \
    libjack-jackd2-dev

USER surge

RUN cd ~/surge/ && /usr/bin/cmake -Bbuildpy -DSURGE_BUILD_PYTHON_BINDINGS=True -DCMAKE_BUILD_TYPE=Release
RUN cd ~/surge/ && /usr/bin/cmake --build buildpy --target surgepy --config Release --target surge-staged-assets
RUN cd ~/surge/ && /usr/bin/cmake --build buildpy --config Release --target surge-staged-assets

# Copy example files
COPY example.py /home/surge/example.py
COPY run.py /home/surge/run.py

# Install Surge locally and set PYTHONPATH
RUN mkdir -p /home/surge/.local/share/surge
RUN echo "export PYTHONPATH=\"$PYTHONPATH:/home/surge/surge/buildpy/src/surge-python\"" >> /home/surge/.bashrc

# /home/surge/surge/buildpy/src/surge-python/

# Switch back to root user
USER root

# Install Python packages
RUN pip3 install --upgrade tqdm ipython numpy soundfile python-slugify

# Clean up unnecessary packages and files
#RUN apt-get remove -y libcairo2-dev libxkbcommon-x11-0 libxkbcommon-dev libxcb-cursor-dev libxcb-keysyms1-dev libxcb-util-dev git build-essential cmake gcc && \
#    apt-get autoclean && \
#    apt-get autoremove -y && \
#    rm -rf /var/lib/apt/lists/*

# Set ownership of home directory
RUN chown -R surge:surge /home/surge/

# Switch back to surge user
USER surge
