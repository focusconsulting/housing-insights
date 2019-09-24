FROM continuumio/miniconda3

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY test_env.yml .

# Install dependencies
RUN conda env create -f test_env.yml 

## Have environment activate on start
RUN echo "source activate housing-insights; cd /repo/back_end" > ~/.bashrc
ENV PATH /opt/conda/envs/housing-insights/bin:$PATH

WORKDIR /repo/back_end
CMD ["python", "app.py"] 
EXPOSE 5000
