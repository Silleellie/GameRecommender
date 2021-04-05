from setuptools import setup, find_packages

setup(
    name='game-recommender',
    version='1.0',
    packages=find_packages(),
    py_modules=['Clustering_usage', 'NaiveRecommender_usage'],
    url='',
    license='',
    author='Anto e Fede',
    author_email='',
    description='',
    python_requires='>=3.5',
    install_requires=[
        'requests>=2.3.0',
        'pandas~=1.0.5',
        'scipy~=1.6.0',
        'sklearn~=0.0',
        'scikit-learn~=0.24.1',
        'tqdm~=4.56.0',
        'regex~=2020.11.13',
        'steamspypi~=1.1.0',
        'igdb-api-v4~=0.0.3',
        'wheel~=0.36.2'
    ]
)
