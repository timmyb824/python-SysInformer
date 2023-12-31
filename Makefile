run-app:
	@echo "Running app via local config"
	python src/main.py run -a

run-pre-commit:
	@echo "Running pre-commit"
	pre-commit run --all-files

run-coverage-tests:
	@echo "Running coverage tests"
	coverage run -m pytest -xv tests/

run-coverage-report:
	@echo "Running coverage report"
	coverage report -m

ignore-pre-commit:
	@echo "Ignoring pre-commit"
	git commit --no-verify -m "$(msg)"

add-deps:
	@echo "Adding dependencies: $(pkg)"
	poetry add $(pkg)
	pip-compile --resolver=backtracking -o requirements.txt pyproject.toml
