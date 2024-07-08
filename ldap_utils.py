from ldap3 import Server, Connection, ALL, SUBTREE
from config import Config
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
def authenticate_user(username, password):
    try:
        server = Server(Config.LDAP_SERVER, port=Config.LDAP_PORT, get_info=ALL)
        admin_conn = Connection(server, user=Config.LDAP_USER, password=Config.LDAP_PASSWORD, auto_bind=True)
       
        search_filter = f'(sAMAccountName={username})'
        admin_conn.search(Config.LDAP_BASE, search_filter, search_scope=SUBTREE, attributes=['distinguishedName'])
       
        if len(admin_conn.entries) == 0:
            logging.warning(f"User not found: {username}")
            return False
       
        user_dn = admin_conn.entries[0].distinguishedName.value
       
        user_conn = Connection(server, user=username, password=password, auto_bind=True)
       
        if user_conn.bound:
            logging.info(f"Authentication successful for user: {username}")
            return True
        else:
            logging.warning(f"Authentication failed for user: {username}")
            return False
   
    except Exception as e:
        logging.error(f'Authentication error: {e}')
        return False

def get_user_details(username):
    try:
        server = Server(Config.LDAP_SERVER, port=Config.LDAP_PORT, get_info=ALL)
        conn = Connection(server, user=Config.LDAP_USER, password=Config.LDAP_PASSWORD, auto_bind=True)
        search_filter = f'(sAMAccountName={username})'
        conn.search(search_base=Config.LDAP_BASE, search_filter=search_filter, attributes=['cn', 'distinguishedName', 'memberOf'])
        if len(conn.entries) > 0:
            user_entry = conn.entries[0]
            cn = user_entry.cn.value if 'cn' in user_entry else None
            distinguished_name = user_entry.entry_dn
            ou = None
            if distinguished_name:
                parts = distinguished_name.split(',')
                for part in parts:
                    if part.startswith('OU='):
                        ou = part.split('=')[1]
                        break
            user_details = {
                'username': username,
                'cn': cn,
                'ou': ou,
                'groups': [str(group) for group in user_entry.memberOf] if 'memberOf' in user_entry else []
            }
            return user_details
        else:
            return None
    except Exception as e:
        print(f'Error retrieving user details: {e}')
        return None