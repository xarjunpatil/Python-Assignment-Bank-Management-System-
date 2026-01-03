#import external modeules
import random
import os
import pyttsx3
# Text file for persistent storage
datafile = "data.txt"
# container for bank database
bankdb = {}
# Text To Speech
engine = pyttsx3.init()
# Load existing data from text file
def loaddb():
    if os.path.exists(datafile):
        try:
            with open(datafile, 'r', encoding='utf-8') as f:
                currentaccount = None
                currentdata = {}
                in_transactions = False
                for line in f:
                    line = line.strip()
                    if line.startswith("Account:"):
                        # Save previous account data if exists
                        if currentaccount and currentdata:
                            bankdb[currentaccount] = currentdata
                        # Start new account
                        currentaccount = line.split(": ")[1]
                        currentdata = {}
                        in_transactions = False
                    elif line.startswith("Name:"):
                        currentdata["name"] = line.split(": ")[1]
                    elif line.startswith("PIN:"):
                        currentdata["pin"] = line.split(": ")[1]
                    elif line.startswith("Balance:"):
                        currentdata["balance"] = int(line.split(": ")[1])
                    elif line == "Transactions:":
                        currentdata["transactions"] = []
                        in_transactions = True
                    elif line == "---END---":
                        in_transactions = False
                    elif in_transactions and line:
                        currentdata["transactions"].append(line)
                # Save the last account
                if currentaccount and currentdata:
                    bankdb[currentaccount] = currentdata
        except Exception as e:
            print(f"Error loading data: {e}")
            return {}
    return bankdb
# Save data to text file
def savedb():
    try:
        with open(datafile, 'w', encoding='utf-8') as f:
            for accountnumber, data in bankdb.items():
                f.write(f"Account: {accountnumber}\n")
                f.write(f"Name: {data['name']}\n")
                f.write(f"PIN: {data['pin']}\n")
                f.write(f"Balance: {data['balance']}\n")
                f.write("Transactions:\n")
                for transaction in data.get('transactions', []):
                    f.write(f"{transaction}\n")
                f.write("---END---\n\n")
    except Exception as e:
        print(f"Error saving data: {e}")
# Load database at startup
bank_db = loaddb()
#mini statement limit
MaxTransacions = 5
#function - create account
def createaccount():
    print("\n===== CREATE NEW ACCOUNT =====")
    # Account holder name with validation
    while True:
        name = input("Enter your full name: ").strip()
        if not name.replace(" ", "").isalpha():
            print("Name must contain only Alphabets. Try again...")
            engine.say("Name must contain only Alphabets. Try again...")
            engine.runAndWait()
            continue
        break
    # Account number input with validation
    while True:
        accountnumber = input("Create your Account Number: ").strip()
        if not (accountnumber.isdigit() and (len(accountnumber) == 10)):
            print("Account number must contain only 10 digits Nothing Else. Try again...")
            engine.say("Account number must contain only 10 digits Nothing Else. Try again...")
            engine.runAndWait()
            continue
        break
    # tiny human-check: avoid empty account number
    if not accountnumber:
        print("Account number cannot be empty...")
        engine.say("Account number cannot be empty...")
        engine.runAndWait()
        return
    if accountnumber in bank_db:
        print("Account already exists! Try a different number...")
        engine.say("Account already exists! Try a different number...")
        engine.runAndWait()
        return
    password = str(random.randint(1000, 9999))
    print( "This Password is Suggested - ", password)
    # PIN must be 4 digits only with validation
    while True:
        pin = input("Set your 4-digit PIN: ").strip()
        if not (pin.isdigit() and len(pin) == 4):
            print("PIN must be exactly 4 digits. Try again...")
            engine.say("PIN must be exactly 4 digits. Try again...")
            engine.runAndWait()
            continue
        confirmpin = input("Re-enter PIN: ").strip()
        if pin != confirmpin:
            print("PIN mismatch! Try again...")
            engine.say("PIN mismatch! Try again...")
            engine.runAndWait()
            continue
        break
    # Storing account details
    bankdb[accountnumber] = {
        "name": name if name else "Unknown",
        "pin": pin,
        "balance": 0,
        "transactions": []
    }
    savedb()  # Save to text file
    print("\nAccount created successfully..!")
    engine.say("Account created successfully..!")
    engine.runAndWait()
    print("Welcome, " + bankdb[accountnumber]["name"] + "!")
    print("======================================")
#function - login
def login():
    print("\n===== LOGIN TO YOUR ACCOUNT =====")
    acc = input("Enter Account Number: ").strip()
    pin = input("Enter PIN: ").strip()
    # small human-style check
    if acc == "" or pin == "":
        print("Please enter both account number and PIN...")
        engine.say("Please enter both account number and PIN...")
        engine.runAndWait()
        return None
    if acc in bankdb and bankdb[acc]["pin"] == pin:
        print(f"\nLogin Successful! Welcome {bankdb[acc]['name']}.\n")
        engine.say(f"Login Successful! Welcome {bankdb[acc]['name']}")
        engine.runAndWait()
        return acc
    else:
        print("Invalid Account Number or PIN..!")
        engine.say("Invalid Account Number or PIN..!")
        engine.runAndWait()
        return None
#function - check balance
def checkbalance(acc):
    print("\n===== BALANCE ENQUIRY =====")
    try:
        holder = bankdb[acc]['name']
        bal = bankdb[acc]['balance']
    except Exception:
        print("Account data not found...")
        engine.say("Account data not found...")
        engine.runAndWait()
        return
    # mixed formatting - human style
    print("Account Holder: " + holder)
    print("Available Balance: " + "₹" + str(bal))
    print("======================================")
#function - mini statement
def ministatement(acc):
    print("\n===== MINI STATEMENT =====")
    transactions = bankdb.get(acc, {}).get("transactions", [])
    if len(transactions) == 0:
        print("No transactions found..!")
        engine.say("No transactions found..!")
        engine.runAndWait()
    else:
        # show most recent last (common human mistake: varying order)
        for t in transactions[-MaxTransacions:]:
            print(t)
    print("======================================")
#function - deposite money
def deposit(acc):
    print("\n===== DEPOSIT MONEY =====")
    amtstr = input("Enter amount to deposit: ").strip()
    try:
        amount = int(float(amtstr))  # tolerate "100.0" etc
    except Exception:
        print("Invalid amount! Please enter a number...")
        engine.say("Invalid amount! Please enter a number...")
        engine.runAndWait()
        return
    if amount <= 0:
        print("Invalid amount..!")
        engine.say("Invalid amount..!")
        engine.runAndWait()
        return
    # update balance + transactions (human style: no atomicity)
    bankdb[acc]["balance"] = bankdb[acc]["balance"] + amount
    bankdb[acc]["transactions"].append("Deposited ₹" + str(amount))

    # Keep last 5 transactions only
    if len(bankdb[acc]["transactions"]) > MaxTransacions:
        # pop older ones
        while len(bankdb[acc]["transactions"]) > MaxTransacions:
            bankdb[acc]["transactions"].pop(0)
    savedb()  # Save to text file
    print("Amount Deposited Successfully!")
    engine.say("Amount Deposited Successfully!")
    engine.runAndWait()
    print("======================================")
#function - withdraw money
def withdraw(acc):
    print("\n===== WITHDRAW MONEY =====")
    amt = input("Enter amount to withdraw: ").strip()
    try:
        amount = int(float(amt))
    except Exception:
        print("Invalid amount! Please enter a number...")
        engine.say("Invalid amount! Please enter a number...")
        engine.runAndWait()
        return
    if amount <= 0:
        print("Invalid amount..!")
        engine.say("Invalid amount..!")
        engine.runAndWait()
        return
    if amount > bankdb[acc]["balance"]:
        print("Insufficient balance..!")
        engine.say("Insufficient balance..!")
        engine.runAndWait()
        return
    bankdb[acc]["balance"] -= amount
    bankdb[acc]["transactions"].append("Withdrawn ₹" + str(amount))
    # cut transactions (human style loop removed with slice)
    if len(bankdb[acc]["transactions"]) > MaxTransacions:
        bankdb[acc]["transactions"] = bank_db[acc]["transactions"][-MaxTransacions:]
    savedb()  # Save to text file
    print("Please collect your cash..!")
    engine.say("Please collect your cash..!")
    engine.runAndWait()
    print("======================================")
#function - change pin
def changepin(acc):
    print("\n===== CHANGE PIN =====")
    oldpin = input("Enter current PIN: ").strip()
    if oldpin != bankdb[acc]["pin"]:
        print("Incorrect PIN..!")
        engine.say("Incorrect PIN..!")
        engine.runAndWait()
        return
    newpin = input("Enter new PIN: ").strip()
    confirmpin = input("Re-enter new PIN: ").strip()
    if newpin != confirmpin:
        print("PIN mismatch..!")
        engine.say("PIN mismatch..!")
        engine.runAndWait()
        return
    bankdb[acc]["pin"] = newpin
    savedb()  # Save to text file
    print("PIN updated successfully!")
    engine.say("PIN updated successfully!")
    engine.runAndWait()
    print("======================================")
#main ATM menu after login
def atmmenu(acc):
    while True:
        print("\n====== ATM MAIN MENU ======")
        print("1. Check Balance")
        print("2. Deposit")
        print("3. Withdraw")
        print("4. Mini Statement")
        print("5. Change PIN")
        print("6. Logout")
        choice = input("Enter your choice: ").strip()
        if choice == "1":
            checkbalance(acc)
        elif choice == "2":
            deposit(acc)
        elif choice == "3":
            withdraw(acc)
        elif choice == "4":
            ministatement(acc)
        elif choice == "5":
            changepin(acc)
        elif choice == "6":
            print("Logged out successfully..!")
            engine.say("Logged out successfully..!")
            engine.runAndWait()
            break
        else:
            # human-ish typo tolerance
            if choice.lower() in ("q", "quit", "exit"):
                print("Logged out successfully..!")
                engine.say("Logged out successfully..!")
                engine.runAndWait()
                break
            print("Invalid option! Try again...")
            engine.say("Invalid option! Try again...")
            engine.runAndWait()
# main program loop
def main():
    try:
        while True:
            print("\n======================================")
            print("          WELCOME TO PYTHON ATM       ")
            print("======================================")
            print("1. Create New Account")
            print("2. Login to Existing Account")
            print("3. Exit")
            userchoice = input("Enter your choice: ").strip()
            if userchoice == "1":
                createaccount()
            elif userchoice == "2":
                loggedinacc = login()
                if loggedinacc:
                    atmmenu(loggedinacc)
            elif userchoice == "3" or userchoice.lower() in ("q", "quit", "exit"):
                print("Thank you for using Python ATM..!")
                engine.say("Thank you for using Python ATM..!")
                engine.runAndWait()
                break
            else:
                print("Invalid selection! Try again...")
                engine.say("Invalid selection! Try again...")
                engine.runAndWait()
    finally:
        # Ensure data is saved even if program crashes
        savedb()
#main function
main()