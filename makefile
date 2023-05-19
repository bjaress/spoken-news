
code=$(shell find api -type f)
unit_tests=$(shell find test -type f)
features=$(shell find features -type f)

test_log=./built/test.log
docker_tag=./built/image.tag
docker_hash=./built/image.hash
docker_name=us-central1-docker.pkg.dev/spoken-news/app-repo/app-image
# TODO something cleaner?

deploy=./built/terraform.backup

.PHONY : test deploy clean

test : $(test_log)

clean :
	rm -rf built/*

$(test_log) : docker/docker-compose.yml docker/Dockerfile.tests \
		$(features) $(docker_hash)
	docker-compose -f docker/docker-compose.yml \
		--no-ansi up --build --no-color --remove-orphans \
		--exit-code-from app-tests | tee $@
	docker-compose -f docker/docker-compose.yml down --remove-orphans | tee -a $@


$(docker_hash) $(docker_tag) : docker/Dockerfile $(code) $(unit_tests) \
		requirements.txt requirements-dev.txt .dockerignore
	docker build --iidfile $(docker_hash) --file docker/Dockerfile .
	# Allow building on a with uncommitted changes, but don't tag for push unless
	# it's clean.
	[ -z "`git status --porcelain`" ] \
		&& echo -n git_ > $(docker_tag) \
		&& git rev-parse --verify HEAD >> $(docker_tag) \
		|| echo -n '' > $(docker_tag)



deploy : $(deploy)

$(deploy) : ./built/terraform.plan
	./terraform apply -backup=$@ $<

./built/terraform.plan : main.tf ./built/docker.push.log $(docker_tag)
	./terraform plan -var "docker_image=$(docker_name):`cat $(docker_tag)`" -out=$@

./built/docker.push.log : $(test_log) $(docker_hash) $(docker_tag)
	# Fail on missing tag (due to uncommitted changes during docker build)
	[ -n "`cat $(docker_tag)`" ] || ( rm $(docker_tag) ; exit 1 )

	docker tag `cat $(docker_hash)` $(docker_name):`cat $(docker_tag)`
	PATH="${PWD}/docker:${PATH}" docker --debug --config docker push \
		"$(docker_name):`cat $(docker_tag)`" | tee $@
