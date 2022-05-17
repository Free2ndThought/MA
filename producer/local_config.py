import os.path

from cryptography import fernet
import json

SETUP_NR = 0
USE_CREDENTIALS = True

if USE_CREDENTIALS:
    with open('.credentials.auth', 'rb') as cred_file:
        with open('.k.ey', 'rb') as key_file:
            key = key_file.read()
        f = fernet.Fernet(key)
        credentials_enc = cred_file.read()
        CREDENTIALS = json.loads(f.decrypt(credentials_enc))
else:
    CREDENTIALS = None

devicelist = list(range(1,2))
#devicelist.remove(4)
#devicelist.remove(14)
#devicelist.remove(30)
DEVICE_LIST = [
    #[1,2,3,5,6,7,8,9,10],
    #[1,2,3,4,5,6,7,8,9,10],
    devicelist,
    #[1,2,3,4,5,6,7,8,9,10],
]

def configure_authentication() -> dict:
    username = input('Username:')
    password = input('Password: ')

    return {'username': username, 'password': password}

# use this to create key and insert credentials
if __name__ == '__main__':

    if os.path.exists('.k.ey'):
        with open('.k.ey', 'rb') as key_file:
            key = key_file.read()
    else:
        f = fernet.Fernet.generate_key()

    f = fernet.Fernet(key)
    credentials_dec = configure_authentication()

    with open('.credentials.auth', 'wb') as cred_file:
        cred_file.write(f.encrypt(json.dumps(credentials_dec).encode('utf-8')))
        cred_file.close()