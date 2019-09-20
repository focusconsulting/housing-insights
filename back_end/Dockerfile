FROM continuumio/miniconda3

MAINTAINER Jason Haas <jasonrhaas@gmail.com>

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY test_env.yml .

# Install dependencies (needs updating)
RUN conda env create -f test_env.yml

# Make sure that the environment updates appropriately
RUN conda env update -n housing-insights -f test_env.yml
#RUN pip install -r requirements.txt

# Activate environment
RUN echo "export PATH=/opt/conda/envs/housing-insights/bin:$PATH" >> /root/.bashrc
RUN cd /repo/back_end/; export FLASK_APP=new_app.py

EXPOSE 5000
