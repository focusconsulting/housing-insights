---
layout: main
title: H.I. Onboarding
---

# Front end development setup

Currently we are doing our development in the `/javascript` folder using simple static HTML pages. While most of the code can be run by simply opening the appropriate file (e.g. `/javascript/tool/map-view.html`), some javascript code needs to access local files. In most browsers this raises a crossorigin request error. The best way around this is to run a local webserver. 

1) Open a command prompt, and change into the javascript folder: 

    cd \path\to\your\housinginsights\javascript

2) Check if you have Python installed already:

    python --version

3a) If you have Python 2.XX, type this:
    
    python -m SimpleHTTPServer

3b) If you have Python 3.XX, type this:
    
    python -m http.server

### Installing Python

If you don't already have Python, we recommend [Miniconda](https://conda.io/miniconda.html), which is a version of Anaconda but that is a smaller download because it doesn't have all the extra packages pre-installed. Anaconda is useful because it allows you to install multiple Python versions and manage virtual environments, so it's what we recommend for our back end team. Select the Python 3.XX version.


