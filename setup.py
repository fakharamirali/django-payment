from payment import __version__
from setuptools import setup, find_packages

setup(
    name='payment',
    version=__version__,
    packages=find_packages(),
    url='https://github.com/fakharamirali/django-payment.git',
    license='BSD 3-Clause License',
    author='Amirali Fakhar',
    author_email='fakharamirali@gmail.com',
    description='This library created for django payment portal',
    include_package_data=True,
    python_requires=">=3.10",
    install_requires=['django>=5.0', 'requests>=2', 'setuptools'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        "Environment :: Web Environment",
        'Framework :: Django',
        'Framework :: Django :: 5.0',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
