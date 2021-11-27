"""
See: https://github.com/pypa/sampleproject/blob/master/setup.py
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the version from nice_cut/version.py without importing the package (inspired by youtube-dl)
exec(compile(open('nice_cut/version.py').read(),
             'nice_cut/version.py', 'exec'))

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='NiceCut',
    version=__version__,
    description='A tool cutting a media file into small clips according to the subtitle file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nlpsuge/NiceCut',
    author='nlpsuge',

    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Desktop Environment',
        "Topic :: Utilities",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
    keywords='python, ffmpeg, media, python3, subtitle, srt-subtitles, cutting, english-learning',
    packages=find_packages(include=['nice_cut', 'nice_cut.*']),
    python_requires='>=3',

    install_requires=[
        'alive_progress>=2.0.0',
    ],

    entry_points={  # Optional
        'console_scripts': [
            'nice-cut = nice_cut.main:main',
            'ncut = nice_cut.main:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/nlpsuge/NiceCut/issues',
        'Source': 'https://github.com/nlpsuge/NiceCut',
    },
)