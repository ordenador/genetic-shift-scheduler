VENV=./venv/bin
PIP=$(VENV)/pip
PYTHON=$(VENV)/python
PIPCOMPILE=$(VENV)/pip-compile
AUTOPEP8=$(VENV)/autopep8
PYCODESTYLE=$(VENV)/pycodestyle
PYLINT=$(VENV)/pylint

.PHONY: help venv pip-compile dev autopep8 pycodestyle check pylint clean run build

define install_package
	$(PIP) list | grep $(1) || $(PIP) install $(1)
endef

help: ## Display this help message
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf " \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

venv: ## Create a virtual environment
	test -x `which virtualenv` || pip install --upgrade virtualenv
	touch requirements.txt
	test -d venv || virtualenv --python=python3 venv

pip-compile: venv ## Upgrade pip, pip-tools, compile requirements
	$(PIP) install --upgrade pip
	$(PIP) install --upgrade pip-tools
	touch requirements.in
	$(PIPCOMPILE) --annotate --upgrade --output-file requirements.txt requirements.in
	$(PIP) install -r requirements.txt

dev: pip-compile ## Install dev requirements

autopep8: ## Auto-format Python files
	$(call install_package,autopep8)
	$(AUTOPEP8) -i *.py --max-line-length 120

pycodestyle: dev ## Check pycodestyle standards
	$(call install_package,pycodestyle)
	find . -mindepth 1 -maxdepth 2 -name '*.py' | xargs $(PYCODESTYLE)

check: pycodestyle pylint ## Check python lint

pylint: dev ## Check pylint standards
	$(call install_package,pylint)
	find . -mindepth 1 -maxdepth 2 -name '*.py' | xargs $(PYLINT)

clean: ## Remove the virtual environment
	find . \( -iname '*.pyc' -o -iname '__pycache__' \) -delete
	rm -rf venv

run: ## Run the app using the virtual environment
	. $(VENV)/activate; python app.py
