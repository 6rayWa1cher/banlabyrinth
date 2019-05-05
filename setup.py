from setuptools import setup, find_namespace_packages

setup(
    name='banlabyrinth',
    version='0.1.0',
    packages=find_namespace_packages(where='src'),
    package_dir={'': 'src'},
    install_requires=[
        'discord.py==1.0.1',
        'appdirs==1.2.0'
    ],
    url='https://github.com/6rayWa1cher/banlabyrinth',
    license='MIT License',
    author='6rayWa1cher',
    entry_points={
        'console_scripts': [
            'banlabyrinth = banlabyrinth.bot:main',
        ]
    },
    author_email='info@a6raywa1cher.com',
    description='This bot supplies your discord server with new temporary ban strategy. Annoying people could be'
                ' trapped inside the labyrinth.',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
