FROM continuumio/miniconda3

# Set up code directory
#RUN mkdir -p /usr/src/app
#WORKDIR /usr/src/app

COPY . /app
WORKDIR /app

# Install dependencies
RUN conda env create -f environment.yml 

## Have environment activate on start
RUN echo "source activate housing-insights;" > ~/.bashrc
ENV PATH /opt/conda/envs/housing-insights/bin:$PATH
#WORKDIR /repo/back_end
EXPOSE 5000
CMD ["python", "app.py"] 
