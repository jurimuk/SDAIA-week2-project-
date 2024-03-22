#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 21 14:38:19 2024

@author: alnwd
"""
#Import library
import json
import os
import datetime
import calendar


def load_users(file_path):
    try:
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                users = json.load(file)
        else:
            users = {}
    except (FileNotFoundError) as e:
        print(f"Error: while accessing file: {e}")
    return users

# Function to save users to a JSON file----------------------------------------------------


def save_users(users, file_path):
    try:
        with open(file_path, "w") as file:
            json.dump(users, file, indent=4)
    except FileNotFoundError:
        print("Error: file path does not exist.")

# Function for user signup----------------------------------------------------------------------


class InvalidPasswordLengthException(Exception):
    pass  # for custom Exception


def signup(users):
    username = input("Enter your username: ")
    if username in users:
        print("Username already exists. Try logging in instead")
        return

    while True:
        password = input("Enter your password (minimum 6 characters): ")
        try:  # Validate password length (of custom exception)
            if len(password) < 6:
                raise InvalidPasswordLengthException(
                    "Password must be at least 6 characters long.")
            break  # Exit while loop after successful validation
        except InvalidPasswordLengthException as e:
            print(e)
    users[username] = {'password': password,
                       'transactions': {'expenses': [], 'income': []}}
    print("You Are Signed up!")

# Function for user login -------------------------------------------------------------------


def login(users):
    username = input("Enter your username: ")
    if username not in users:
        print("your username isn't correct")
    password = input("Enter your password: ")
    if users[username]['password'] == password:    # Check if the password is correct

        print("Login successful!")
        return username
    else:
        print("Login failed. Please check your username and password.")
        return None

# Function to add transaction (expense or income)----------------------------------------------------


class InvalidDateFormatException(Exception):
    pass

class Transaction:
    def add_transaction(self, user_data, transaction_type):
        try:
            amount = float(input(f"Enter the amount {transaction_type}: "))
            category = input(f"Enter the category for {transaction_type}: ")

            while True:
                date = input("Enter the date (YYYY-MM-DD): ")
                try:
                    # Validate date format and range
                    date_obj = datetime.datetime.strptime(date, "%Y-%m-%d")

                    # Exception for invalid month (1-12)
                    if not 1 <= date_obj.month <= 12:
                        raise ValueError("Invalid month. Please enter a month between 1 and 12.")

                    # Exception for invalid year (1900 - 2024)
                    if not 1900 <= date_obj.year <= 2024:
                        raise ValueError("Invalid year. Please enter a year between 1900 and 2024.")

                    # Check for valid day based on month using the calendar library
                    if not 1 <= date_obj.day <= calendar.monthrange(date_obj.year, date_obj.month)[1]:
                        raise ValueError("Invalid day. Please enter a correct day for the chosen month.")

                    break  # Exit loop when the entered date is correct

                except ValueError as e:
                    print(f"Invalid date format or value: {e}")

            transaction = {'amount': amount, 'category': category, 'date': date}
            user_data['transactions'][transaction_type].append(transaction)
            print(f"{transaction_type.capitalize()} added successfully!")

        except Exception as e:
            print(f"An error occurred: {e}")

# Function to view transactions
class InvalidChoiceError(Exception):
    pass

def view_transactions(user_data):
    print("\n1. View Expenses")
    print("2. View Income")
    print("3. Back")

    while True:  # Loop until a valid choice is entered
        try:
            choice = input("Enter your choice: ")
            if choice in ('1', '2', '3'):
                break  # Exit loop.
            else:
                raise InvalidChoiceError(
                    "Invalid choice. Please mind the options (1-3).")
        except InvalidChoiceError as e:
            print(e)  # Print error message

    # Rest of the function logic for processing the valid choice
    if choice == '1':
        print("\nExpenses:")
        sort_transactions(user_data['transactions']['expenses'], choice=choice)
    elif choice == '2':
        print("\nIncome:")
        sort_transactions(user_data['transactions']['income'], choice=choice)
    elif choice == '3':
        return


def sort_transactions(transactions, choice=None):
    sorting_options = {
        "1": ("date", "Date (Older to Newer)"),  # Use "date" for sorting key
        # Use "date" for sorting key (reversed later)
        "2": ("date", "Date (Newer to Older)"),
        # Use "amount" for sorting key (reversed later)
        "3": ("amount", "Amount (High to Low)"),
        # Use "amount" for sorting key
        "4": ("amount", "Amount (Low to High)"),
    }

    if choice in ('1', '2'):
        # Display sort options only for expenses (1) or income (2)
        print("\nSort Options:")
        for key, value in sorting_options.items():
            print(f"{key}. {value[1]}")
        sort_by = input(
            "Choose sorting option (1-4) or press Enter for default (date ascending): ")

        # Validate and use the chosen sorting option (or default)
        if sort_by:
            if sort_by in sorting_options:
                # Use description for message
                sort_message = sorting_options[sort_by][1]
                # Use first element of tuple for sorting key
                sort_key = sorting_options[sort_by][0]
                # Reverse order for date descending and amount descending
                if sort_by in ("2", "3"):
                    sorted_transactions = sorted(
                        transactions, key=lambda x: x[sort_key], reverse=True)
                else:
                    sorted_transactions = sorted(
                        transactions, key=lambda x: x[sort_key])
            else:
                print("Invalid choice. Using default (date ascending).")
                sorted_transactions = sorted(
                    transactions, key=lambda x: x['date'])  # Default sorting
        else:
            sorted_transactions = transactions  # No sorting chosen

    else:
        # No sorting options for other choices
        sorted_transactions = transactions

    # Display sorting message
    print(
        f"\nTransactions sorted by: {sort_message if sort_by else 'Date (Older to Newer)'}")

    for transaction in sorted_transactions:
        print(
            f"Amount: {transaction['amount']}, Category: {transaction['category']}, Date: {transaction['date']}")


# Function to delete transaction
def delete_transaction(user_data):
    transaction_type = input(
        "Enter the type of transaction (expense or income): ").lower()
    transactions = user_data['transactions'][transaction_type]
    print(f"Select the {transaction_type} to delete:")
    for i, transaction in enumerate(transactions):
        print(
            f"{i + 1}. Amount: {transaction['amount']}, Category: {transaction['category']}, Date: {transaction['date']}")
    try:
        index = int(input("Enter the index of the transaction to delete: ")) - 1
        if 0 <= index < len(transactions):
            del transactions[index]
            print("Transaction deleted successfully!")
        else:
            print("Invalid index.")
    except ValueError:
        print("Invalid index.")

# Function to generate basic reports
def generate_reports(user_data):
    expenses = user_data['transactions']['expenses']
    income = user_data['transactions']['income']

    total_expenses = sum(transaction['amount'] for transaction in expenses)
    total_income = sum(transaction['amount'] for transaction in income)

    print(f"\nTotal Expenses: ${total_expenses}")
    print(f"Total Income: ${total_income}")

    categories = {}
    for transaction in expenses:
        category = transaction['category']
        categories[category] = categories.get(
            category, 0) + transaction['amount']

    print("\nSpending by Category:")
    for category, amount in categories.items():
        print(f"{category}: ${amount}")

# Main function
def main():
    users_file = "users.json"
    users = load_users(users_file)
    transaction_instance = Transaction()
    
    while True:
        print("\n1. Signup")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")

        if choice == '1':
            signup(users)
        elif choice == '2':
            username = login(users)
            if username: 
                user_data = users[username]
                while True:
                    print("Please Choose the transaction type:")
          
                    print("1. Add an Expense")
                    print("2. Add an Income")
                    
                    option = input("Enter your option: ")
                
                    if option == '1':
                        transaction_instance.add_transaction(user_data, 'expenses')
                        break
                    elif option == '2':
                        transaction_instance.add_transaction(user_data, 'income')
                        break
                    else:
                        print("Invalid option. Please try again.")

                while True:
                    print("1. View Transactions")
                    print("2. Delete Transaction")
                    print("3. Generate Reports")
                    print("4. Save Transactions")
                    print("5. Logout")
                    option1 = input("Enter your option: ")
                    
                    if option1 == '1':
                        view_transactions(user_data)
                    elif option1 == '2':
                        delete_transaction(user_data)
                    elif option1 == '3':
                        generate_reports(user_data)
                    elif option1 == '4':
                        save_users(users, users_file)
                    elif option1 == '5':
                        break
                    else:
                        print("Invalid option. Please try again.")
        elif choice == '3':
            save_users(users, users_file)  
            print("Goodbye! have a good day ! :)")
            break
        else:
            print("Invalid choice. Please enter a valid option.")

if __name__ == "__main__":
    main()