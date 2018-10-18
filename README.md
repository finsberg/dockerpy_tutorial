# Python Docker API tutorial

Sometimes you just want to run a software within your application in order to get some output, and preferable without having to install the software itself and all its dependencies. Say for example that you need to solve a PDE in order to get some information about the physics and that you want to use [FEniCS](https://fenicsproject.org) for that. Now FEniCS can be quite complicated to install, and therefore it would be nice if we could use some of the [pre-built docker images](https://fenics-containers.readthedocs.io/en/latest/index.html).
One thing you could do is run your application inside one of the pre-built containers, but this might not be ideal for all use-cases.

What I will show you, is how you can spin up a container on the fly within your application in order to e.g solve your PDE inside a container and then just throw away the container once you are done. You can achieve this using the [Python Docker API](https://github.com/docker/docker-py).

## Example problem

As an example I will look at a problem that is taken for a Cardiac Mechanics benchmark which looks at a bending beam. The basis of this is example can be found in the [following example](https://finsberg.github.io/pulse/html/demos/problem1.html) which uses a library called [`pulse`](https://finsberg.github.io/pulse) which is based on FEniCS to solve the mechanics. However, I want to make this example only depend upon FEniCS, and therefore I will strip away any `pulse` dependency. However, if you are interested is more mechanics demos please check out the [`pulse` repository](https://github.com/finsberg/pulse)

The problem is as follow: Say that we have a beam of size 1x1x10 mm^3, which we apply some traction on the bottom of the beam which will bend the beam. We want to know how much it bends if we apply a certain amount of traction.
Furthermore, we want to do so using the docker API.


## Installation

Before you get started we need to install the python docker API. First make sure that you have [installed Docker](https://docs.docker.com/install/).
Next create a virtual environment and install the API.

```shell
virtualenv venv
pip install docker
```

## Running the api
In this repo you will find a python script called [`api.py`](api.py). This contains the code for creating a running a container inside python. It will run the script [`bending_beam.py`](bending_beam.py). It will also mount a folder called `output` as a  volume inside the container so that any files you save inside the container will be saved to your local computer in the folder called `output`.

When you run
```
python api.py
```
It will launch a container and run the `bending_beam.py` script. Once it is done you will find some new files in the `output` folder which you can inspect later.
