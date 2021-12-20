import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="expetator",
    version="0.3.7",
    author="Georges Da Costa",
    author_email="georges.da-costa@irit.fr",
    description="A framework for monitoring HPC applications using DVFS",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/georges-da-costa/expetator",
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
    install_requires=['execo'],

)
