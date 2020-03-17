from RSA_General import encrypt
from RSA_General import decrypt
import sqlite3
import hashlib

public_key = (4351, 7081)
private_key = (2815, 7081)
d = private_key[0]
e = public_key[0]
n = public_key[1]


def is_valid_pin_length(a):
    if len(a) != 4:
        return False
    else:
        return True


def set_pin(a):
    pin = input("Set PIN\n")
    if not is_valid_pin_length(pin):
        print("Invalid PIN Length! Enter Valid PIN!")
        while not is_valid_pin_length(pin):
            pin = input("Set PIN\n")
    pin_hash = hashlib.sha512(pin.encode())
    conn = sqlite3.connect("AccountsInfo.db")
    cur = conn.execute("UPDATE Accounts SET Pin = ? WHERE Card_No = ?", (str(pin_hash.hexdigest()), str(a)))
    conn.commit()
    conn.close()


def is_valid_pin(card_no, a):
    user_pin_decrypted = decrypt(a[1], private_key[0], private_key[1])
    conn = sqlite3.connect("AccountsInfo.db")
    cmd = "SELECT * FROM Accounts WHERE Card_No = "+card_no
    cur = conn.execute(cmd)
    for row in cur:
        if row[5] == str(hashlib.sha512(user_pin_decrypted.encode()).hexdigest()):
            return True
    return False


def withdrawal(card):
    conn = sqlite3.connect("AccountsInfo.db")
    cmd = "SELECT * FROM Accounts WHERE Card_No = "+str(card)
    cur = conn.execute(cmd)
    for row in cur:
        if row[5] is None:
            set_pin(card)
        else:
            pin_user = input("Enter PIN\n")
            if is_valid_pin(card, encrypt(pin_user, public_key[0], public_key[1])):
                amount = float(input("ENTER AMOUNT TO WITHDRAW\n"))
                balance = row[4] - amount
                if balance < 0:
                    print("Not Sufficient Balance!!")
                else:
                    cmd = "UPDATE Accounts SET Amount = "+str(balance)+" WHERE Card_No = "+str(card)
                    cur.execute(cmd)
                    print("Transaction Successful!")
                    print("Available Balance: ", balance)
            else:
                print("Incorrect PIN!")
    conn.commit()
    conn.close()


def check_balance(a):
    conn = sqlite3.connect("AccountsInfo.db")
    cmd = "SELECT * FROM Accounts WHERE Card_No = "+str(a)
    cur = conn.execute(cmd)
    for row in cur:
        if row[5] is None:
            set_pin(a)
        else:
            pin_user = input("Enter PIN\n")
            if is_valid_pin(a, encrypt(pin_user, public_key[0], public_key[1])):
                print("Balance: ", row[4])
            else:
                print("Incorrect PIN!")
    conn.commit()
    conn.close()


def change_pin(a):
    conn = sqlite3.connect("AccountsInfo.db")
    cmd = "SELECT * FROM Accounts WHERE Card_No = "+str(a)
    cur = conn.execute(cmd)
    for row in cur:
        if row[5] is None:
            set_pin(a)
        else:
            pin_user = input("Enter PIN\n")
            if is_valid_pin(a, encrypt(pin_user, public_key[0], public_key[1])):
                set_pin(a)
            else:
                print("Incorrect PIN!")
    conn.commit()
    conn.close()


def if_record_exists(a):
    conn = sqlite3.connect("AccountsInfo.db")
    cur = conn.cursor()
    cmd = "SELECT * FROM Accounts WHERE Card_No = " + str(a)
    for row in cur.execute(cmd):
        return True
    return False


print("***************WELCOME***************")
card_num = input("ENTER CARD NUMBER\n")
if not if_record_exists(card_num):
    print("No Records Found!")
else:
    task = int(input("1. Withdraw \n2. Check Balance\n3. Change PIN\n"))
    if task == 1:
        withdrawal(card_num)
    elif task == 2:
        check_balance(card_num)
    elif task == 3:
        change_pin(card_num)
