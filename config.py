class Config:
    LDAP_SERVER = 'ldap://sahil.com'
    LDAP_PORT = 389
    LDAP_USER = 'CN=Admin,DC=sahil,DC=com'
    LDAP_PASSWORD = 'Ongc1234'
    LDAP_BASE = 'DC=sahil,DC=com'
    SECRET_KEY = 'Saol2'
    SQLALCHEMY_DATABASE_URI = 'mysql://root:sahil@localhost/final'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
