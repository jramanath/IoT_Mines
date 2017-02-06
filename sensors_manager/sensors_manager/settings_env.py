# -*- coding: utf-8 -*-
"""
Template pour settings_env.py

Les lignes où un commentaire indique "TODO" sont à modifier en fonction
de l'environnement.  Une fois que vous avez mis les bonnes valeurs, enlevez
le TODO, et ce paragraphe-ci ;)
"""

# email et password de l'utilisateur "admin"
ADMIN_EMAIL = "DL-SGDBF_Services_Intermediation@saint-gobain.com"
ADMIN_PASSWORD = 'admin'  # TODO: remplacer par une valeur aléatoire

# où sont les logs
LOGS_DIR = 'C:/Users/J9051014/Documents/Point.P/api_data/log/'  # TODO: remplacer par le bon chemin

# où est le virtualenv python ?
PYTHON_VENV_DIR = '/path/to/venv'  # TODO: remplacer par le bon chemin

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'p1ursiqkkhd&5z!&bf100^^d_7*mrn4fbss&1e*$g-)_ehnt3r'
# TODO: remplacer par une autre chaîne de caractère aléatoire

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True  # NE PAS TOUCHER pour le moment... mais un jour peut-être !

# Quelle est l'adresse qu'on sert ?
ALLOWED_HOSTS = ['*']  # TODO: demander, "intermed(-[a-z]*)?.homly-you.com"

# Où se trouvent les fichiers avec les données initiales ?
INITIAL_DATA_DIR = ''  # TODO: chemin vers le dossier /data
# 'C:/Users/J9051014/Documents/Point.P/api_data/initial_data/'

# Où se trouve le cache à utiliser pour le SEA ?
CACHE_SEA_DIR = 'C:/Users/J9051014/Documents/Point.P/api_data/cache_sea/'

# Où préparer les fichiers statiques ?
STATIC_ROOT = '/path/to/static'  # TODO: chemin vers le dossier /appli/static

# Configuration des bases de données
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'intermediation_jacques',   # TODO: database mysql
        'USER': 'root',   # TODO: user mysql
        'PASSWORD': 'monchantier',  # TODO: password mysql
        'HOST': 'a98cl051web10t.hosts.pointp.saint-gobain.net',  # TODO: host mysql
        'TEST': {
            'NAME': 'intermed_test',  # TODO: database mysql cree lors de tests
            'CHARSET': 'utf8',
            'COLLATION': 'utf8_general_ci',
        },
    }
}


# Accès à Salesforce
SALESFORCE = {
    'USERNAME': '',  # TODO: demander, "[a-z.]+@saint-gobain.com(.[a-z]*)?"
    'PASSWORD': '',  # TODO: demander
    'TOKEN': '',  # TODO: demander
    'SANDBOX': True,  # TODO: False en prod, True partout ailleurs
}

SUPERVISION_EMAIL = ''
DEFAULT_FROM_EMAIL = ''
