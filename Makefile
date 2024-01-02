build:
	pipenv install --dev

format:
	pipenv run black --line-length 120 .

lint:
	pipenv run flake8 --config setup.cfg .

typecheck:
	pipenv run mypy .

gen:
	pipenv run python src/__init__.py --file_mode=gen

evaluate:
	pipenv run python src/__init__.py --file_mode=test

evaluate-values:
	pipenv run python src/__init__.py --file_mode=test-values

analyze:
	pipenv run python src/__init__.py --file_mode=analyze