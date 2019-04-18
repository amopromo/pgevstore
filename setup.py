import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pgevstore",
    version="0.0.1",
    author="Waltton",
    author_email="waltton@2xt.com.br",
    description="Event storage based on PostgreSQL",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amopromo/pgevstore",
    packages=['pgevstore', 'pgevstore.client', 'pgevstore.pgpart'],
    classifiers=[],
    entry_points={
        'console_scripts': ['pgpart=pgevstore.pgpart:main'],
    },
    install_requires=[
        'psycopg2-binary',
    ],
)
