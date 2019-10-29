FROM continuumio/miniconda3

# Set up code directory
# Leave for deployment
COPY ./environment.yml /app/environment.yml
WORKDIR /app

# Install dependencies
RUN conda env create -f environment.yml 

COPY . /app

## Have environment activate on start
RUN echo "source activate housing-insights;" > ~/.bashrc
ENV PATH /opt/conda/envs/housing-insights/bin:$PATH

# Run the app and send it to localhost
EXPOSE 5000
CMD ["python", "app.py"] 
