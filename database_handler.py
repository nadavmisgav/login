#!/usr/bin/python

from getpass import getpass, getuser
import hashlib, binascii
from os import urandom
import re
import MySQLdb
import sys, traceback

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def get_username():
    while True:
        user_name = raw_input('Username: ')
        if len(user_name) == 0:
            print "Username is required!"
            continue
        if len(user_name) > 20:
            print "Username can not be more then 20 characters!"
            continue
        if (re.search("""[^0-9a-zA-Z]""", user_name)):
            print "Username can contain only characters and digits!"
            continue
        break
    return user_name

def get_password(prompt='Password'):
    while True:
        usr_pass = getpass(prompt)
        if len(usr_pass) < 6:
            print "Password must contain 6 characters or more!"
            continue
        if not (re.search('[a-zA-Z]', usr_pass) and re.search('[0-9]', usr_pass)):
            print "Password must contain digits and charcters!"
            continue
        return usr_pass

def get_usr_pwd():
    while True:

        salt = urandom(32)
        dk = hashlib.pbkdf2_hmac('sha256', get_password("Enter your password: "), salt, 1000000)
        hashed_pass = binascii.hexlify(dk)
        dk = hashlib.pbkdf2_hmac('sha256', get_password("Re-enter your password: "), salt, 1000000)
        current_hashed_pass = binascii.hexlify(dk)
        if hashed_pass == current_hashed_pass:
            return hashed_pass, salt
            break
        print "Passwords do not match! Please retry."

def check_usr_pwd(hashed_pwd, salt):
    for i in xrange(1,4):
        usr_pwd_attempt = hashlib.pbkdf2_hmac('sha256', getpass(), salt, 1000000)
        hashed_attempt = binascii.hexlify(usr_pwd_attempt)
        if hashed_pwd == hashed_attempt:
            return True
    return False

def create_user():
    """Creates user returns True if succeeded False otherwise"""

    print bcolors.OKBLUE + "Register" + bcolors.ENDC
    try:
        db = MySQLdb.connect("localhost","root","qwerty","test")
        cursor = db.cursor()
    except:
        traceback.print_exc(file=sys.stdout)
        return False

    while True:
        user_name = get_username()
        cursor.execute("select user_name from users where user_name='%s';" % user_name)
        data = cursor.fetchall()
        if len(data) == 0:
            break
        else:
            print "Username taken!"

    while True:
        email = raw_input('Email [optional]: ')
        if (re.search("""[^0-9a-zA-Z\.@]""", email)):
            print "Email can not contain special characters!"
            continue
        else:
            break
    hashed_pass, salt = get_usr_pwd()

    try:
        cursor.execute("""insert into users (user_name, email, password, salt)
        values ("%s", "%s", "%s", "%s");""" % (user_name, email, hashed_pass, salt))
        db.commit()
    except:
        print bcolors.FAIL + "Failed creating user!" + bcolors.ENDC
        traceback.print_exc(file=sys.stdout)
        db.rollback()
        db.close()
        return False

    print bcolors.OKGREEN+ "User registerd!" + bcolors.ENDC
    return True

def login():

    print bcolors.OKBLUE + "Login" + bcolors.ENDC
    try:
        db = MySQLdb.connect("localhost","root","qwerty","test")
        cursor = db.cursor()
    except:
        traceback.print_exc(file=sys.stdout)
        return False
    while True:
        user_name = get_username()
        try:
           cursor.execute("""select password, salt from users where user_name="%s";""" % user_name)
           data =  cursor.fetchall()
           if len(data) == 0:
               print "No such user!"
               continue
           break
        except:
            print bcolors.FAIL + "Failed getting user!" + bcolors.ENDC
            traceback.print_exc(file=sys.stdout)
            db.close()
            return False

    db.close()
    password, salt = data[0]
    status = check_usr_pwd(password, salt)
    if status:
        print bcolors.OKGREEN+ "User authenticated!" + bcolors.ENDC
    else:
        print bcolors.FAIL + "User failed to authenticate!" + bcolors.ENDC
    return True

def show_users():
    try:
        db = MySQLdb.connect("localhost","root","qwerty","test")
        cursor = db.cursor()
        cursor.execute("""select user_name from users;""")
        for user_name in cursor.fetchall():
            print user_name[0]

    except:
        traceback.print_exc(file=sys.stdout)
        db.close()
        return False

    db.close()
    return True

def delete_user():
    print bcolors.OKBLUE + "Delete user" + bcolors.ENDC
    user_name = get_username()
    try:
        db = MySQLdb.connect("localhost","root","qwerty","test")
        cursor = db.cursor()
        cursor.execute("""select * from users where user_name='%s';""" % user_name)
        data = cursor.fetchall()
        if len(data) == 0:
            print bcolors.FAIL + "Username does not exist!" + bcolors.ENDC
            return True
        user_id, user_name, _, password, salt = data[0]
        print "Are you sure you want to delete"
        print "%s\t%s" % (user_id, user_name)
        print "to delete enter users password:"
        status = check_usr_pwd(password, salt)
        if status:
            cursor.execute("""delete from users where id=%d""" % user_id)
            db.commit()
            print bcolors.OKGREEN + ("%s was deleted!" % user_name) + bcolors.ENDC
            return True
        else:
            print bcolors.FAIL + "Password did not match, user was not deleted." + bcolors.ENDC
            return True

    except:
        traceback.print_exc(file=sys.stdout)
        db.rollback()
        db.close()
        return False

    db.close()
    return True

def admin_cli():
    print bcolors.OKBLUE + "Admin CLI" + bcolors.ENDC
    try:
        db = MySQLdb.connect("localhost","root","qwerty","test")
        cursor = db.cursor()
        cursor.execute("""select password, salt from users where user_name='root';""")
        data = cursor.fetchall()
        if len(data) == 0:
            print 'An admin account is not available!'
        password, salt = data[0]
        status = check_usr_pwd(password, salt)
        if status:
            while True:
                try:
                    command = raw_input('>>> ')
                    if command == 'exit':
                        break
                    if command == '':
                        continue
                    cursor.execute(command)
                    db.commit()
                    for row in cursor.fetchall():
                        print row
                except:
                    db.rollback()
                    traceback.print_exc(file=sys.stdout)

    except:
        traceback.print_exc(file=sys.stdout)
        db.close()
        return False

    db.close()
    return True

def main():

    while True:
        print bcolors.OKBLUE + "Choose operation:" + bcolors.ENDC
        print "1) Create new user"
        print "2) Login"
        print "3) Print all users"
        print "4) Delete user"
        print "5) Admin CLI"
        print "or type 'q' to quit"
        option = raw_input(">>> ")

        if option  == "1":
            create_user()
        elif option == "2":
            login()
        elif option == "3":
            show_users()
        elif option == "4":
            delete_user()
        elif option == "5":
            admin_cli()
        elif option == "q":
            return 0
        else:
            print "Incorrect option!"

if __name__ == "__main__":
    main()
