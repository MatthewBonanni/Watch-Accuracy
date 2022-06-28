Bootstrap: docker

From: python:3

%files
watchperf.py /

%post
    #This is based on debian buster...
    #apt-get update --fix-missing && apt-get install -y python-pip git openjdk-11-jdk
    cd /
    
    python3 -m pip install ntplib python-dateutil tabulate

%runscript
    exec python3 /watchperf.py "$@"
    #exec snipit "$@"

