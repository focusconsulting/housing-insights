FROM continuumio/miniconda3

MAINTAINER Jason Haas <jasonrhaas@gmail.com>

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

# Copy over files
COPY environment.yml .
COPY requirements.txt .

# Install dependencies
RUN conda env create

# Activate environment
RUN echo "export PATH=/opt/conda/envs/housing-insights/bin:$PATH" >> /root/.bashrc
