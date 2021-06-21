TAG := ${CI_COMMIT_REF_NAME}

.PHONY: tests

tests:
	docker build -t test .
	docker run --entrypoint pytest test

build:
	docker build --network=host . -t ${TAG}

push-image:
	docker push ${TAG}
