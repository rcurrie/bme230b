"""
Tooling to spin up hosts running jupyter on Azure for BME230B
"""
import os
import glob
import json
import datetime
from fabric.api import env, local, run, sudo, runs_once, parallel, warn_only, cd, settings
from fabric.operations import put, get

# To debug communication issues un-comment the following
# import logging
# logging.basicConfig(level=logging.DEBUG)


def _find_machines():
    """ Fill in host globals from docker-machine """
    env.user = "ubuntu"
    machines = [json.loads(open(m).read())["Driver"]
                for m in glob.glob(os.path.expanduser("~/.docker/machine/machines/*/config.json"))]
    env.hostnames = [m["MachineName"] for m in machines
                     if not env.hosts or m["MachineName"] in env.hosts]
    env.hosts = [local("docker-machine ip {}".format(m["MachineName"]), capture=True) for m in machines
                 if not env.hosts or m["MachineName"] in env.hosts]
    print(env.hosts)
    env.key_filename = [m["SSHKeyPath"] for m in machines]
    # Use single key due to https://github.com/UCSC-Treehouse/pipelines/issues/5
    # env.key_filename = "~/.ssh/id_rsa"


_find_machines()


@runs_once
def cluster_up(count=1):
    """ Spin up 'count' docker machines """
    print("Spinning up {} more cluster machines".format(count))
    for i in range(int(count)):
        hostname = "bme230b-{:%Y%m%d-%H%M%S}".format(datetime.datetime.now())
        local("""
              docker-machine create --driver azure \
		--azure-subscription-id "11ef7f2c-6e06-44dc-a389-1d6b1bea9489" \
		--azure-location "westus" \
		--azure-ssh-user "ubuntu" \
		--azure-open-port 80 \
		--azure-size "Standard_D16_v3" \
		--azure-resource-group "bme230bstudents" \
              {}
              """.format(hostname))

    # In case additional commands are called after up
    _find_machines()


def configure_machines():
    run("sudo chown ubuntu:ubuntu /mnt")
    run("sudo usermod -aG docker ${USER}")
    put("class")
    # run("chmod -R +r-w class/")


@runs_once
def cluster_down():
    """ Terminate ALL docker-machine machines """
    for host in env.hostnames:
        print("Terminating {}".format(host))
        local("docker-machine stop {}".format(host))
        local("docker-machine rm -f {}".format(host))


@runs_once
def machines():
    """ Print hostname, ip, and ssh key location of each machine """
    print("Machines:")
    for machine in zip(env.hostnames, env.hosts):
        print("{}/{}".format(machine[0], machine[1]))

def ps():
    run("docker ps")


def jupyter_up():
    """ Launch a jupyter notebook server on each cluster machine """
    run("""
	nohup docker run -d --name jupyter \
		--user root \
		-e JUPYTER_ENABLE_LAB=1 \
		-e GRANT_SUDO=yes \
		-e NB_UID=`id -u` \
		-e NB_GID=`id -g` \
		-p 80:8888 \
		-v `echo ~`:/home/jovyan \
		-v /mnt:/scratch \
		robcurrie/jupyter start-notebook.sh \
		--NotebookApp.password='sha1:c708a30ae9da:674e576d9a1b4c7fb421ea8b26e972cc63b93e59'
	""", pty=False)

def jupyter_down():
    """ Shutdown the jupyter notebook server on each cluster machine """
    with warn_only():
        run("docker stop jupyter && docker rm jupyter")
