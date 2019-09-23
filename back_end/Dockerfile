FROM continuumio/miniconda3

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY test_env.yml .

# Install dependencies
RUN conda env create -f test_env.yml 
RUN echo "source activate housing-insights" > ~/.bashrc
## Activate environment
ENV PATH /opt/conda/envs/housing-insights/bin:$PATH

EXPOSE 5000
