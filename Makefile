build:
	docker build --rm -t robcurrie/bme230b .

jupyter:
	# Run jupyter notebook on local machine - change password to your own
	docker run --rm -it --name jupyter \
		--user root \
		-e JUPYTER_ENABLE_LAB=1 \
		-e GRANT_SUDO=yes \
		-e NB_UID=`id -u` \
		-e NB_GID=`id -g` \
		-p 80:8888 \
		-v `echo ~`:/home/jovyan \
		-v /mnt:/scratch \
		jupyter/tensorflow-notebook start-notebook.sh \
		--NotebookApp.password='sha1:c708a30ae9da:674e576d9a1b4c7fb421ea8b26e972cc63b93e59'

upload:
	docker run -it -v ${HOME}:/root microsoft/azure-cli
	az storage blob upload -c data --name tcga_target_gtex.h5 --file ~/tcga_target_gtex.h5
