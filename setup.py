"""
See: https://github.com/pypa/sampleproject/blob/master/setup.py
"""

from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()

# Get the version from good_tailor/version.py without importing the package (inspired by youtube-dl)
exec(compile(open('good_tailor/version.py').read(),
             'good_tailor/version.py', 'exec'))

long_description = (here / 'README.md').read_text(encoding='utf-8')

setup(
    name='GoodTailor',
    version=__version__,
    description='A tool cutting a media file into small clips according to the subtitle file',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/nlpsuge/GoodTailor',
    author='nlpsuge',

    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Desktop Environment',
        "Topic :: Utilities",
        "Topic :: Multimedia :: Video :: Conversion",
    ],
    keywords='python, ffmpeg, media, python3, subtitle, srt-subtitles, cutting, english-learning',
    packages=find_packages(include=['good_tailor', 'good_tailor.*']),
    python_requires='>=3',

    install_requires=[
        'alive_progress>=1.6.1',
    ],

    entry_points={  # Optional
        'console_scripts': [
            'good-tailor = good_tailor.main:main',
            'gt = good_tailor.main:main',
        ],
    },

    project_urls={
        'Bug Reports': 'https://github.com/nlpsuge/GoodTailor/issues',
        'Source': 'https://github.com/nlpsuge/GoodTailor',
    },
)