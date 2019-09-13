import setuptools

setuptools.setup(
    name             = 'bpfeeder',
    version          = '0.0.1',
    install_requires = ['investpy', 'yahoofinancials'],
    description      = 'Datafeeder for Financidal Data Collection',
    author           = 'Kim jinho',
    author_email     = 'blackpaper9973@gmail.com',
    url              = 'https://github.com/blackpaper9973/bpfeeder',
    download_url     = 'https://githur.com/blackpaper9973/bpfeeder/archive/master.gz',
    packages         = ['bpfeeder'],
    keywords         = ['financial data', 'quant'],
    python_requires  = '>=3',
    zip_safe         = False
)