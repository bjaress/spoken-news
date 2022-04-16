
features=$(shell find features -type f)
test_log=./built/test.log


$(test_log) : docker-compose.yml Dockerfile.tests $(features)
	docker-compose --no-ansi up --build --no-color --remove-orphans \
		| tee $@
	docker-compose down | tee -a $@
