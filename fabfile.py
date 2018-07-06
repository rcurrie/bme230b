"""
Tooling to spin up hosts running jupyter on Azure for BME230B
"""
import os
import glob
import json
import datetime
import pprint
from StringIO import StringIO
from fabric.api import env, local, run, sudo, runs_once, parallel, warn_only, cd, settings
from fabric.operations import put, get
from fabric.contrib.console import confirm

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
    # env.key_filename = [m["SSHKeyPath"] for m in machines]
    # Use single key due to https://github.com/UCSC-Treehouse/pipelines/issues/5
    # env.key_filename = [m["SSHKeyPath"] for m in machines]
    env.key_filename = "~/.ssh/id_rsa"



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
		--azure-size "Standard_D8_v3" \
		--azure-storage-type "Standard_LRS" \
		--azure-resource-group "bme230bstudents" \
              {}
              """.format(hostname))
        local("cat ~/.ssh/id_rsa.pub" +
              "| docker-machine ssh {} 'cat >> ~/.ssh/authorized_keys'".format(hostname))

    # In case additional commands are called after up
    _find_machines()

@parallel
def configure_machines():
    """ Push out class templates and download data sets """
    run("sudo usermod -aG docker ${USER}")

    put("class")

    run("sudo chown ubuntu:ubuntu /mnt")
    run("mkdir -p /mnt/data /mnt/scratch")
    with cd("/mnt/data"):
        # run("wget -r -np -R 'index.html*' -N https://bme230badmindiag811.blob.core.windows.net/data/") 
        run("wget -q -N https://bme230badmindiag811.blob.core.windows.net/data/tcga_target_gtex_train.h5") 
        run("wget -q -N https://bme230badmindiag811.blob.core.windows.net/data/tcga_mutation_train.h5") 
        run("wget -q -N https://bme230badmindiag811.blob.core.windows.net/data/breast-cancer-wisconsin.data.csv") 
        run("wget -q -N https://bme230badmindiag811.blob.core.windows.net/data/c2.cp.kegg.v6.1.symbols.gmt") 
        run("wget -q -N https://bme230badmindiag811.blob.core.windows.net/data/tcga_mutation_test_unlabeled.h5") 
    run("sudo chown ubuntu:ubuntu /mnt")

    run("""sudo docker pull robcurrie/jupyter | grep -e 'Pulling from' -e Digest -e Status -e Error""")
    # run("chmod -R +r-w class/")


@runs_once
def cluster_down():
    """ Terminate ALL docker-machine machines """
    if confirm("Stop and delete all cluster machines?", default=False):
        for host in env.hostnames:
            print("Terminating {}".format(host))
            with warn_only():
                local("docker-machine stop {}".format(host))
            with warn_only():
                local("docker-machine rm -f {}".format(host))


@runs_once
def machines():
    """ Print hostname, ip, and ssh key location of each machine """
    print("Machines:")
    for machine in zip(env.hostnames, env.hosts):
        print("{}/{}".format(machine[0], machine[1]))

def ps():
    """ List dockers running on each machine """
    run("docker ps")


def jupyter_up():
    """ Launch a jupyter notebook server on each cluster machine """
    with warn_only():
        run("""
            nohup docker run -d --name jupyter \
                    --user root \
                    -e JUPYTER_ENABLE_LAB=1 \
                    -e GRANT_SUDO=yes \
                    -e NB_UID=`id -u` \
                    -e NB_GID=`id -g` \
                    -p 80:8888 \
                    -v `echo ~`:/home/jovyan \
                    -v /mnt/data:/home/jovyan/data \
                    -v /mnt/scratch:/scratch/home/jovyan/data \
                    robcurrie/jupyter start-notebook.sh \
                    --NotebookApp.password='sha1:c708a30ae9da:674e576d9a1b4c7fb421ea8b26e972cc63b93e59'
            """, pty=False)

def jupyter_down():
    """ Shutdown the jupyter notebook server on each cluster machine """
    with warn_only():
        run("docker stop jupyter && docker rm jupyter")

def backhaul():
    """ Backhaul notebooks from all the cluster machines into /mnt/students """
    username = env.host
    with warn_only():
        fd = StringIO()
        paths = get("~/username.txt", fd)
        if paths.succeeded:
            username=fd.getvalue().strip()
    local("mkdir -p /mnt/students/{}".format(username))
    local("rsync -av --max-size=10m --delete ubuntu@{}:~/* /mnt/students/{}".format(env.host, username))
    # with cd("/mnt/students/{}".format(username)):
    #     get("/home/ubuntu/*", "/mnt/students/{}/".format(username))
