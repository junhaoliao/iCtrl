import pyDes

KEY = [232, 74, 214, 96, 196, 114, 26, 224]
CRYPT = pyDes.des(KEY)


def obfuscate_password(password):
    padded_raw = (password + '\0' * 8)[:8]
    return CRYPT.encrypt(padded_raw)


def decrypt_passwd(obfuscated):
    decrypted_bytes = CRYPT.decrypt(obfuscated)
    return decrypted_bytes.decode("ascii").rstrip('\0')


def vncpasswd(passwd_path, password=None):
    if password is None:
        obfuscated = read_password()
    else:
        obfuscated = obfuscate_password(password)

    with open(passwd_path, "wb") as passwd:
        passwd.write(obfuscated)

    return obfuscated


def vncpasswd2plain(passwd_path):
    with open(passwd_path, "rb") as passwd:
        return decrypt_passwd(passwd.readline())


def read_password():
    from getpass import getpass
    while True:
        passwd = getpass("Password: ")
        if len(passwd) == 0:
            print("Password not changed")
            exit(1)
        elif len(passwd) < 6:
            print("Password must be at least 6 characters - try again")
            continue

        passwd2 = getpass("Verify: ")
        if passwd != passwd2:
            print("Passwords don't match - try again")
            continue
        return obfuscate_password(passwd)
