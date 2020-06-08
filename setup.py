from setuptools import setup, find_packages

setup(
    name='flask_utils',
    description=(
        'flask-utils to provide common tools, '
        'RoutingSQLAlchemy(read-write split for flask-sqlalchemy), Form, Serializer, LoopCall'
    ),
    author='Charles',
    author_email='huiran_shi@126.com',
    url='https://github.com/charlesxs/flask-utils',
    license="BSD",
    zip_safe=False,
    keywords='flask sqlalchemy master slave form serializer',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    version='1.0',
    packages=find_packages(),
    install_requires=['flask-sqlalchemy==2.4.1', 'sqlalchemy==1.3.10', 'psycopg2-binary==2.8.4']
)
