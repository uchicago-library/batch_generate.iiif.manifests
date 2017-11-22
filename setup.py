from setuptools import setup

setup(
    name="generating_iiif_manifests",
    author="Tyler Danstrom",
    author_email="tdanstrom@uchicago.edu",
    version="2.0.0",
    license="LGPL3.0",
    description="A command-line script to generate IIIF Manifests", 
    keywords="python3.5 iiif-presentation manifests",
    scripts=['bin/generate-iiif.py'],
    classifiers=[
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Operating System :: POSIX :: Linux",
        "Topic :: Text Processing :: Markup :: XML",
    ]
)
