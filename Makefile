build:
	docker build --rm -t robcurrie/bme230b .

push:
	docker push robcurrie/bme230b

upload:
	docker run -it -v ${HOME}:/root microsoft/azure-cli
	az storage blob upload -c data --name tcga_target_gtex.h5 --file ~/tcga_target_gtex.h5

nbviewer:
	docker run -d \
		-v /mnt/students:/notebooks \
		-p 8080:8080 \
		jupyter/nbviewer \
		python3 -m nbviewer --port=8080 --no-cache --localfiles=/notebooks
