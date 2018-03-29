from setuptools import setup

setup(
    name="generating_iiif_manifests",
    author="Tyler Danstrom",
    author_email="tdanstrom@uchicago.edu",
    version="2.0.0",
    license="LGPL3.0",
    description="A command-line script to generate IIIF Manifests", 
    keywords="python3.5 iiif-presentation manifests",
    scripts=['bin/generate-iiif.py',
             'bin/break_mvol4_subsorts_into_multi_records.py' ,
             'bin/build_collection_manifest.py',
             'bin/check_map_marc_metadata.py',
             'bin/convert_maps_html_table_to_json.py',
             'bin/copy_tifs_to_iiif.py',
             'bin/create_speculum_cho_dirs.py',
             'bin/create_speculum_itineraries.py',
             'bin/find_chisoc_maps.py',
             'bin/find_social_scientists.py',
             'bin/fix_image_urls.py',
             'bin/generate_apf_iiif.py',
             'bin/generate_maps_iiifs.py',
             'bin/make_mvol4_collection_record.py',
             'bin/make_rac_manifests.py',
             'bin/make_speculum_collection.py',
             'bin/organize_chopin_chos.py',
             'bin/organize_goodspeed.py',
             'bin/subsort_mvol4_by_year.py'

    ],
    classifiers=[
        "License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Operating System :: POSIX :: Linux",
        "Topic :: Text Processing :: Markup :: XML",
    ]
)
