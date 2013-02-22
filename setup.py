import os
from setuptools import (
    setup,
    find_packages,
)


version = '0.1'
shortdesc = "Python source file abstraction based on nodes"
longdesc = open(os.path.join(os.path.dirname(__file__), 'README.rst')).read()
longdesc += open(os.path.join(os.path.dirname(__file__), 'LICENSE.rst')).read()


setup(name='node.ext.python',
      version=version,
      description=shortdesc,
      long_description=longdesc,
      classifiers=[
          'License :: OSI Approved :: BSD License',
          'Intended Audience :: Developers',
          'Topic :: Software Development',
          'Operating System :: OS Independent',
          'Programming Language :: Python',
      ],
      keywords='',
      author='BlueDynamics Alliance',
      author_email='dev@bluedynamics.com',
      url=u'http://github.com/bluedynamics/node.ext.python',
      license='BSD',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['node', 'node.ext'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'node.ext.directory',
          # -*- Extra requirements: -*
      ],
      extras_require = dict(
          test=[
              'interlude',
          ]
      ),
      entry_points="""
      # -*- Entry points: -*-
      """)
