from setuptools import setup, find_packages

setup(
    name='multi_cafeteria_simulation',
    version='1.0.0',
    description='A multi-cafeteria and multi-window simulation system',
    author='Your Name Here',
    author_email='your.email@example.com',
    packages=find_packages(),
    install_requires=[
        'pytest>=7.0.0',
        'pytest-cov>=4.0.0'
    ],
    python_requires='>=3.7',
)