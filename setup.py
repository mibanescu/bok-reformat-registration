import os

from setuptools import find_packages, setup

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.txt")) as f:
    README = f.read()
with open(os.path.join(here, "CHANGES.txt")) as f:
    CHANGES = f.read()

requires = ["attrs", "flup", "plaster_pastedeploy", "pyramid", "pyramid_jinja2", "pyramid_debugtoolbar", "waitress"]

tests_require = []

setup(
    name="registrationcsv",
    version="0.4",
    description="registrationcsv",
    long_description=README + "\n\n" + CHANGES,
    classifiers=[
        "Programming Language :: Python",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: WSGI :: Application",
    ],
    author="Mihai Ibanescu",
    author_email="mihai.ibanescu@gmail.com",
    url="",
    keywords="web pyramid pylons",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    extras_require={"testing": tests_require},
    install_requires=requires,
    entry_points={"paste.app_factory": ["main = registrationcsv:main"]},
)
