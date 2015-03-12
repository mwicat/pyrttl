from setuptools import setup


setup(name='pyrttl',
      version='0.5.0',
      description='Library for parsing and processing of rttl rintgtones',
      author='mwicat',
      author_email='mwicat@gmail.com',
      packages=['pyrttl'],
      entry_points={'console_scripts':
                        ['rttlproc = pyrttl.scripts.rttlproc:main']
                    }
)
