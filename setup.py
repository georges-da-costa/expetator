import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="expetator",
    version="0.3.23",
    author="Georges Da Costa",
    author_email="georges.da-costa@irit.fr",
    description="A framework for monitoring HPC applications using DVFS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.irit.fr/sepia-pub/expetator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    package_data={'': ['benchmarks/genericbench/*', 'benchmarks/*tpr', 'benchmarks/*.c', 'benchmarks/*.tgz', 'benchmarks/*.cu',
                       'monitors/*.bz2', 'monitors/*.diff',
                       'leverages/*.[ch]', 'leverages/*.sh', 'leverages/*_mak']},
    include_package_data=True,
    install_requires=['execo', 'requests'],
    entry_points={
        'console_scripts': [
            'remove_watermark = expetator.remove_watermark:main',
            'csv_plot = expetator.monitoring_csv:show_csv_main',
            'list_plot = expetator.monitoring_list:show_list_main',
            'add_energy = expetator.add_energy:main',
            'get_nb_freq = expetator.get_nb_freq:main',
            'clean_csv = expetator.clean_csv:main',
        ]
    }


)
