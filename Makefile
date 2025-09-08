#======================#
# Install, clean, test #
#======================#

install_requirements:
	@pip install -r requirements.txt

install:
# @pip install . -U
	@pip install e .

clean:
	@rm -f */version.txt
	@rm -f .coverage
	@rm -fr */__pycache__ */*.pyc __pycache__
	@rm -fr build dist
	@rm -fr proj-*.dist-info
	@rm -fr proj.egg-info

test_structure:
	@bash tests/test_structure.sh

#======================#
#          API         #
#======================#

run_api:
	uvicorn api.fast:app --reload --port 8000


#======================#
#          GCP         #
#======================#

gcloud-set-project:
	gcloud config set project $(GCP_PROJECT)



#======================#
#         Docker       #
#======================#

# Local images - using local computer's architecture
# i.e. linux/amd64 for Windows / Linux / Apple with Intel chip
#      linux/arm64 for Apple with Apple Silicon (M1 / M2 chip)

docker_build_local:
	docker build --tag=$(GAR_IMAGE):local .

docker_run_local:
	docker run \
		-e PORT=8000 -p $(PORT):8000 \
		--env-file .env \
		$(GAR_IMAGE):local

docker_run_local_interactively:
	docker run -it \
		-e PORT=8000 -p $(PORT):8000 \
		--env-file .env \
		$(GAR_IMAGE):local \
		bash

# Cloud images - using architecture compatible with cloud, i.e. linux/amd64

DOCKER_IMAGE_PATH := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(GAR_REPO)/$(GAR_IMAGE)

DOCKER_REPO_PATH := $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(GAR_REPO)

docker_show_image_path:
	@echo $(DOCKER_IMAGE_PATH)

docker_show_repo_path:
	@echo $(DOCKER_REPO_PATH)

docker_list_pushed_images:
	gcloud artifacts docker images list "$(DOCKER_REPO_PATH)" --include-tags \
  	--format='table(image,tags)'

docker_list_images:
	docker image ls $(DOCKER_IMAGE_PATH)

docker_build:
	docker build \
		--platform linux/amd64 \
		-t $(DOCKER_IMAGE_PATH):prod .

# Alternative if previous doesn´t work. Needs additional setup.
# Probably don´t need this. Used to build arm on linux amd64
docker_build_alternative:
	docker buildx build --load \
		--platform linux/amd64 \
		-t $(DOCKER_IMAGE_PATH):prod .

docker_run:
	docker run \
		--platform linux/amd64 \
		-e PORT=8000 -p $(PORT):8000 \
		--env-file .env \
		$(DOCKER_IMAGE_PATH):prod

docker_run_interactively:
	docker run -it \
		--platform linux/amd64 \
		-e PORT=8000 -p $(PORT):8000 \
		--env-file .env \
		$(DOCKER_IMAGE_PATH):prod \
		bash

# Push and deploy to cloud

docker_allow:
	gcloud auth configure-docker $(GCP_REGION)-docker.pkg.dev

docker_create_repo:
	gcloud artifacts repositories create $(GAR_REPO) \
		--repository-format=docker \
		--location=$(GCP_REGION) \
		--description="Repository for storing docker images"

# docker build here before pushing (see above)
docker_push:
	docker push $(DOCKER_IMAGE_PATH):prod

docker_deploy:
	gcloud run deploy \
		--image $(DOCKER_IMAGE_PATH):prod \
		--memory $(GAR_MEMORY) \
		--cpu 4 \
		--region $(GCP_REGION) \
		--env-vars-file .env.yaml
