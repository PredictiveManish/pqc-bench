.PHONY: sources validate groundtruth test all run-example clean

sources:
	python3 scripts/validate_sources.py

validate:
	python3 scripts/validate.py

groundtruth:
	python3 scripts/validate_ground_truth.py

test:
	python3 tests/test_plumbing.py

all: sources validate groundtruth test

run-example:
	python3 scripts/run_eval.py --provider openai --model gpt-4o --k 3 --md results/gpt-4o.md

clean:
	rm -rf results/*.json results/*.md .cache
	find . -name '__pycache__' -type d -prune -exec rm -rf {} +
