from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()

setup(name='ur_cb2',
      version='0.1',
      description='A package to interface with a UR CB2 Robot over TCP/IP',
      long_description=readme(),
      classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Manufacturing',
        'Intended Audience :: Science/Research',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Topic :: Text Processing :: Linguistic',
      ],
      keywords='universal robots cb2 ur5',
      url='-',
      author='Michael Sobrepera',
      author_email='mjsobrep@live.com',
      license='Copyright (c) 2016 GTRC. All rights reserved.',
      packages=['ur_cb2', 'ur_cb2.receive', 'ur_cb2.send'],
      install_requires=[
      ],
      include_package_data=True,
      entry_points={
        'console_scripts': ['cb2-listen=ur_cb2.receive.cb2_receive_example:'
                            'main',
                            'cb2-record=ur_cb2.receive.cb2_store_points:main']
      },
      zip_safe=False)
