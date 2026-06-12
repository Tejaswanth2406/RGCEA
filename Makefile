.PHONY: install test coverage demo lint clean zip

install:
	pip install -e ".[dev]"

test:
	PYTHONPATH=. python -m pytest tests/ -v

coverage:
	PYTHONPATH=. python -m pytest tests/ --cov=rgcea --cov-report=term-missing

demo:
	PYTHONPATH=. python scripts/rgcea_demo.py --cycles 3 --episodes 200 --seed 42

demo-verbose:
	PYTHONPATH=. python scripts/rgcea_demo.py --cycles 5 --episodes 500 --log-level DEBUG

lint:
	python -m py_compile rgcea/**/*.py rgcea/*.py scripts/*.py
	@echo "Syntax OK"

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -name "*.pyc" -delete
	rm -rf .pytest_cache htmlcov .coverage dist build *.egg-info

zip: clean
	cd .. && zip -r rgcea.zip rgcea/ --exclude "rgcea/.git/*"
	@echo "Created ../rgcea.zip"
