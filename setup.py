
from setuptools import setup

with open('README.rst') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(name = 'wzone',
      version = '0.1dev2',
      description = 'Package for making zones of armed conflicts.',
      long_description = readme,
      url='http://github.com/kyosuke-kkt/wzone',
      author='Kyosuke Kikuta',
      author_email='kyosuke.kkt@outlook.com',
      license=license,
      packages=['wzone'],
      package_data={'wzone': ['data/*.pkl',
                              'data/w_date/*.pkl', 'data/w_date/*.gzip',
                              'data/wo_date/*.pkl', 'data/wo_date/*.gzip']},
      zip_safe=False,
      python_requires='>=2.7',
      install_requires=['numpy>=1.11.3', 'pandas>=0.18.1', 'sklearn>=0.0'],
      test_suite='wzone.tests',
      classifiers=['Development Status :: 3 - Alpha',
                   'Environment :: Console',
                   'Intended Audience :: End Users/Desktop',
                   'License :: OSI Approved :: MIT License',
                   'Operating System :: Microsoft :: Windows :: Windows 10',
                   'Operating System :: MacOS :: MacOS X',
                   'Programming Language :: Python :: 2.7',
                   'Topic :: Software Development :: Libraries :: Python Modules'])


