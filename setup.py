# -*- coding: utf-8 -*-
"""Installer for the mpf.portal2026 package."""

from setuptools import find_packages
from setuptools import setup


long_description = "\n\n".join([
    open("README.rst").read(),
    open("CONTRIBUTORS.rst").read(),
    open("CHANGES.rst").read(),
])


setup(
    name='mpf.portal2026',
    version='1.0a1',
    description="Portal MPF 2026",
    long_description=long_description,
    long_description_content_type="text/x-rst",

    classifiers=[
        "Environment :: Web Environment",
        "Framework :: Plone",
        "Framework :: Plone :: Addon",
        "Framework :: Plone :: 5.2",
        "Framework :: Plone :: 6.0",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
    ],
    keywords='Python Plone CMS',
    author='Luis Flavio Rocha',
    author_email='luis.rocha@v2solucoes.com.br',
    url='https://github.com/collective/mpf.portal2026',
    project_urls={
        'PyPI': 'https://pypi.org/project/mpf.portal2026/',
        'Source': 'https://github.com/collective/mpf.portal2026',
        'Tracker': 'https://github.com/collective/mpf.portal2026/issues',
        # 'Documentation': 'https://mpf.portal2026.readthedocs.io/en/latest/',
    },
    license='GPL version 2',
    packages=find_packages('src', exclude=['ez_setup']),
    namespace_packages=['mpf'],
    package_dir={'': 'src'},
    include_package_data=True,
    zip_safe=False,
    python_requires=">=3.7",
    install_requires=[
        'setuptools',
        # -*- Extra requirements: -*-
        'z3c.jbot',
        'plone.api>=1.8.4',
        'plone.app.dexterity',
    ],
    extras_require={
        'test': [
            'plone.app.testing',
            # Plone KGS does not use this version, because it would break
            # Remove if your package shall be part of coredev.
            # plone_coredev tests as of 2016-04-01.
            'plone.testing>=5.0.0',
            'plone.app.contenttypes',
            'plone.app.robotframework[debug]',
        ],
    },
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    [console_scripts]
    update_locale = mpf.portal2026.locales.update:update_locale
    """,
)
