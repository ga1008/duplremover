import setuptools
from setuptools import setup

with open("README.md", "r", encoding='utf-8') as fh:
    long_description = fh.read()

using_setuptools = True

setup_args = {
    'name': 'dupremover',
    'version': '0.0.5',
    'url': 'https://github.com/GuardianGH/duplremover/tree/master/duplremover',
    'description': 'a tool to remove any duplicated files',
    'long_description': long_description,
    'author': 'Guardian',
    'author_email': 'zhling2012@live.com',
    'maintainer': 'Guardian',
    'maintainer_email': 'zhling2012@live.com',
    'long_description_content_type': "text/markdown",
    'LICENSE': 'MIT',
    'packages': setuptools.find_packages(),
    'include_package_data': True,
    'zip_safe': False,
    'entry_points': {
        'console_scripts': [
            'remover = duplremover.duplicate_remover:rmduplicate'
        ]
    },

    'classifiers': [
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    'install_requires': [
        'argparse'
    ],
}

setup(**setup_args)
