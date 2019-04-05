# Overview

This singularity container was modified from 'https://github.com/singularityhub/jupyter' and 'https://github.com/dash00/tensorflow-python3-jupyter'

The purpose of modification was to migrate from Singularity version 2.x to version 3.x (https://www.sylabs.io/guides/3.0/user-guide/). Deep learning and image processings modules along with their dependency were also installed.

## Singularity

If you haven not installed singularity, do that with [these instructions](https://www.sylabs.io/guides/3.0/user-guide/quick_start.html).

## Building a container

1) Download the repo:
```
git clone https://github.com/si-medbif/jupyter-openslide-tflearn
cd jupyter-openslide-tflearn
```      
2) Build the container
```
sudo singularity build jupyter.sif jupyter.def
```

## Run the container

A local path must be mapped to `/opt/notebooks` to work with the notebooks. IP of the local machine or the server hosting the container must be assigned in <x.x.x.x> (e.g. --ip=123.45.67.890). `--NotebookApp.token=''` and  `--NotebookApp.password=''` are for turning off authentication. If you require some security, please change the values.

```   
singularity run -B $PWD/notebooks:/opt/notebooks jupyter.sif --ip=<x.x.x.x> --port=8888 \
      --notebook-dir=/opt/notebooks --allow-root  --no-browser \
      --NotebookApp.token='' --NotebookApp.password=''
```

Singularity 3.x supports `cgroups` for resource limitation. If you are to run the container on a server sharing resources with multiple users, it would be better to use `cgroups`. Using `cgroups` requires `sudo` as shown below

```
sudo singularity run --apply-cgroups path/to/cgroups.toml -B $PWD/notebooks:/opt/notebooks \
      jupyter.sif --ip=<x.x.x.x> --port=8888 --notebook-dir=/opt/notebooks --allow-root  \
      --no-browser --NotebookApp.token='' --NotebookApp.password=''
```

More details regarding `cgroups` in Singularity can be found [here](https://www.sylabs.io/guides/3.0/user-guide/cgroups.html)

## Note on port forwarding (Might not work with Singularity 3.x. Must be checked)

If you are running Singularity in Windows through vagrant. You will need to configure port fowarding in the Vagrantfile that you use to set up the Singularity container as well. 
As an example, you should add a line that might look like this.
`config.vm.network "forwarded_port", guest: 8888, host: 8888, host_ip: "127.0.0.1"`
