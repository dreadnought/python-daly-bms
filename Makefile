package-build:
	python3 setup.py sdist bdist_wheel
	twine check dist/*
package-upload:
	twine upload dist/*
package-commit:
	git commit -m "Version `python3 setup.py --version`"
	git tag "v`python3 setup.py --version`"
	git push
	git push --tags
