
REGISTERED_IMAGES_REPO := "registered-jobs-images"

# Usage: IMAGE_NAME=my-script make build_and_push_image
build_and_push_image:
	docker build -t $(IMAGE_NAME) . -f Dockerfile-$(IMAGE_NAME)
	docker tag $(IMAGE_NAME) $(REGISTRY_BASE_PATH)/$(GCP_PROJECT_ID)/$(REGISTERED_IMAGES_REPO)/$(IMAGE_NAME)
	docker push $(REGISTRY_BASE_PATH)/$(GCP_PROJECT_ID)/$(REGISTERED_IMAGES_REPO)/$(IMAGE_NAME)
