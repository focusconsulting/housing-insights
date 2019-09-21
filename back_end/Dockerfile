FROM continuumio/miniconda3

# Set up code directory
RUN mkdir -p /usr/src/app
WORKDIR /usr/src/app

COPY test_env.yml .

# Install dependencies
RUN conda env create -f test_env.yml \
## Activate environment
&& echo "export PATH=/opt/conda/envs/housing-insights/bin:$PATH" >> ~/.bashrc \
&& conda activate housing-insights \
&& RUN cd /repo/back_end/
CMD ["python", "app.py"]
#RUN cd /repo/back_end/; export FLASK_APP=app.py

EXPOSE 5000
