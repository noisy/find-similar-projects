from setuptools import setup

setup(
    name="find-similar-projects",
    version="0.1.2",
    author='@noisy - Krzysztof Szumny',
    author_email='noisy.pl@gmail.com',
    description='find-similar-projects is simple script, which grep all pip requirements files in all Github repositories.',
    scripts=['find-similar-projects'],
    install_requires=[
        "lxml==4.6.5",
        "termcolor==1.1.0",
    ],
)
