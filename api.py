import docker
import os
import shutil
import threading

traction = 1.0
outfile = 'result.json'

# Create client
cli = docker.from_env()
# Get image
image = cli.images.get('quay.io/fenicsproject/stable:2017.2.0')

outdir = os.path.join(os.getcwd(), 'output')
if not os.path.exists(outdir):
    os.makedirs(outdir)

# Move script to the output folder so that we can run it inside the container
script = 'bending_beam.py'
shutil.copy(script, os.path.join(outdir, script))

# Mount currnet the directory where the fenics script is located to /opt
volumes = {outdir: {'bind': '/fenics/home/shared', 'mode': 'rw'}}
# The command that we should run inside the container
entrypoint = ['python3']
command = [script, str(traction), outfile]

# Create container
container = cli.containers.create(
    image=image,
    entrypoint=entrypoint,
    command=command,
    volumes=volumes,
    name='bending_beam',
    working_dir='/fenics/home/shared'
)


def run_container():
    # Start container
    container.start()
    # Wait until the container is finitshed
    container.wait()
    output = container.logs()
    print(output.decode('utf-8'))
    container.stop()
    container.remove(force=True)

# Run this inside a thread (this is not neccesary but nice if you want
# to do other types of work while the container is running.)
thread = threading.Thread(target=run_container)
thread.start()
