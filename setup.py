from setuptools import setup, find_packages

setup(
    name='payment',
    version='0.0.2',
    packages=find_packages(),
    url='https://github.com/fakharamirali/django-payment.git',
    license='BSD 3-Clause License',
    author='Amirali Fakhar',
    author_email='fakharamirali@gmail.com',
    description='This library created for django payment portal',
    include_package_data=True,
    python_requires=">=3.9",
    install_requires=['django>=4.0', 'requests>=2'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Framework :: Django',
        'Framework :: Django :: 4.0',
        'Framework :: Django :: 4.1',
        'Framework :: Django :: 4.2',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Software Development :: Libraries :: Application Frameworks',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],

)
