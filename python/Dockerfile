FROM continuumio/miniconda3

MAINTAINER Jason Haas <jasonrhaas@gmail.com>

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY environment.yml .
COPY requirements.txt .

# Install dependencies
RUN conda env create -f environment.yml

# Make sure that the environment updates appropriately
RUN conda env update -n housing-insights -f environment.yml

# Activate environment
RUN echo "export PATH=/opt/conda/envs/housing-insights/bin:$PATH" >> /root/.bashrc

EXPOSE 5000