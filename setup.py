from distutils.core import setup

setup(name = "taxodb_ncbi",
    version = "2.0",
    description = (""),
    license='',
    author = "Corinne Maufrais",
    author_email = "corinne.maufrais@pasteur.fr",
    url = "",
    package_dir={'': 'src'},
    packages=[''],
    install_requires = ['golden >= 2', 
	'bdb', 
],
) 
