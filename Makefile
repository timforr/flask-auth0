ifeq ($(PIP_SERVER_HOST),)
	# needed to install package via pip inside the docker container
	PIP_SERVER_HOST=https://pypi.dev.sands.im:4843
endif
PIP=$(PIP_SERVER_HOST)/pypi

pip_upload:
	@echo \> upload to pip server $(PIP)
	python setup.py bdist_wheel upload -r $(PIP)

pip_install:
	@echo \> install locally
	@python setup.py --quiet install

test:
	@echo \> testing
	@tox
