# Własne ustawienia dla środowiska produkcyjnego.
from .base import *

# Jeżeli o tym zapomnisz, ryzykujesz
# wyświetlenie pełnych informacji o stosie wywołań, a także poufnych danych
# konfiguracyjnych, które nie powinny być udostępniane publicznie.
DEBUG = False
# Określa, że żądanie HTTP ma zostać przekierowane do HTTPS.
SECURE_SSL_REDIRECT = True

# Opcja powinna być ustawiona, aby było możliwe utworzenie
# bezpiecznego cookie używanego do ochrony przed atakami typu CSRF.
CSRF_COOKIE_SECURE = True

ADMINS = (
    ('Bihun M', 'mac.bih@wp.pl'),
)

# dla debug = false, do aplikacji można dostać się tylko za pomocą podany hstów
ALLOWED_HOSTS = ['localhost','maciejbihun.com', 'www.maciejbihun.com']

DATABASES = {
        'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'educa',
        'USER': 'educa',
        'PASSWORD': 'maciek1234',
    }
}