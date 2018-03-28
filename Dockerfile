FROM jupyter/datascience-notebook:96f2f777be6e

USER root

RUN apt-get update \
  && apt-get install -y --no-install-recommends \
    curl \
    wget \
    zip \
    zlib1g-dev \
    time \
    samtools \
    bedtools \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://get.docker.com/ | sh
RUN usermod -aG docker jovyan

RUN wget -qO- https://github.com/lomereiter/sambamba/releases/download/v0.6.7/sambamba_v0.6.7_linux.tar.bz2 \
  | tar xj -C /usr/local/bin

# The order of these is intentional to work around conflicts
RUN conda install --yes pytorch torchvision -c pytorch

RUN conda install --yes tensorflow keras

RUN pip install --upgrade pip
ADD requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

RUN conda install --yes numpy==1.14.1 scikit-learn==0.19.0

USER jovyan
