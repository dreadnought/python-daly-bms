package-build:
	python3 setup.py sdist bdist_wheel
	twine check dist/*
package-upload:
	twine upload dist/*
