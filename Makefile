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

guess-the-style:
	pipenv run python src/__init__.py --file_mode=test

guess-the-range:
	pipenv run python src/__init__.py --file_mode=test-values

guess-commercial-examples:
	pipenv run python src/__init__.py --file_mode=test-commercial-examples

analyze:
	pipenv run python src/__init__.py --file_mode=analyze