
code=$(shell find app -type f)
unit_tests=$(shell find test -type f)
features=$(shell find features -type f)
test_log=./built/test.log
docker_image=./built/image.id


$(test_log) : docker-compose.yml Dockerfile.tests $(features) $(docker_image)
	docker-compose --no-ansi up --build --no-color --remove-orphans \
		--exit-code-from app-tests | tee $@
	docker-compose down | tee -a $@


$(docker_image) : Dockerfile $(code) $(unit_tests) \
		requirements.txt requirements-dev.txt
	docker build --iidfile $@ .
