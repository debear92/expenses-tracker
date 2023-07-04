import datetime
import gspread
from google.oauth2.service_account import Credentials

SCOPE = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.file",
    "https://www.googleapis.com/auth/drive"
    ]

CREDS = Credentials.from_service_account_file('creds.json')
SCOPED_CREDS = CREDS.with_scopes(SCOPE)
GSPREAD_CLIENT = gspread.authorize(SCOPED_CREDS)
SHEET = GSPREAD_CLIENT.open('expenses_tracker')


class Expense:
    "Creates an instance of Expense."
    def __init__(self, date, name, amount, category):
        self.date = date
        self.name = name
        self.category = category
        self.amount = amount

    def __repr__(self):
        """
        Returns a printable representational string of the specified object.
        """
        return (
            f"Expense:"
            f"On {self.date} you have spent €{self.amount} for {self.name}"
        )


def main():
    """
    Run program.
    """
    print("Welcome to the Ultimate Expense Tracker! /n")

    while True:
        print("What do you want to do today?")
        print("1. Add a new expense.")
        print("2. View expenses")
        print("3. Calculate total expenses")
        print("4. Exit")

        option = input("Enter your choice: ")
        if option == "1":
            expense = get_expense()
            update_file(expense)
        elif option == "2":
            view_expenses(period)
        elif option == "3":
            calculate_total_expenses()
        elif option == "4":
            print("Thank you for using the Ultimate Expense Tracker! \n"
                  "Have a nice day!")
            break
        else:
            print("Invalid option. Please try again.")


def get_expense():
    """
    Get expense input from user.
    Convert the amounnt input to a float.
    Offer selected categories to choose from.
    """
    while True:
        expense_date = input("Please enter your expense date (DD/MM/YYYY): \n")
        try:
            # Validate expense date format
            datetime.datetime.strptime(expense_date, "%d/%m/%Y")
            break
        except ValueError as e:
            print(
                f"Invalid date: {e}. Please enter the date as DD/MM/YYYY."
                )

    expense_name = input("Please, enter your expense name: \n")

    while True:
        expense_amount = input("Please, enter your expense amount: \n")
        try:
            # Validate expense amount.
            # Check if input is a number and if the number is positive.
            expense_amount = float(expense_amount)
            if expense_amount > 0:
                break
            else:
                print("Invalid amount. Please enter a positive number.")
        except ValueError:
            print("Invalid amount. Please enter a numeric value.")

    expense_categories = [
        "🍕 Food",
        "🏠 Home",
        "💼 Work",
        "💊 Health",
        "🎈 Misc"
    ]

    while True:
        print("Select a category: ")
        for i, category_name in enumerate(expense_categories):
            print(f"  {i + 1}.  {category_name}")
        category_options = f"[1 - {len(expense_categories)}]"
        chosen_index = input(f"Enter a category number {category_options}:")
        try:
            chosen_index = int(chosen_index)
            if chosen_index in range(1, len(expense_categories) + 1):
                selected_category = expense_categories[chosen_index - 1]
                new_expense = Expense(
                    expense_date, expense_name,
                    expense_amount, selected_category)

                return new_expense

            else:
                print("Invalid category. Please try again!")
        except ValueError:
            print(f"{expense_categories} is invalid. \n"
                  "Please enter a numeric value.")
    main()
    

def update_file(expense):
    """
    Update the google sheet with the data provided by the user.
    """
    print(f"Saving User Expense: {expense}")

    # Extract expense attributes
    expense_date = expense.date
    expense_name = expense.name
    expense_amount = expense.amount
    expense_category = expense.category
 
    # Open the expense_tracker worksheet
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")

    # Append expense data to the worksheet
    expense_tracker_sheet.append_row(
        [expense_date, expense_name, expense_amount, expense_category])
    print("User Expense saved successfully\n")
    

def view_expenses(period):
    """
    Allow user to view their previously recorded expenses.
    User can choose if to view all the expenses logged, 
    the expenses for the month or for the day.
    """
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    if period == "all":
        expense_records = expense_tracker_sheet.get_all_records()
    elif period == "month":
        expense_records = get_expenses_for_current_month(expense_tracker_sheet)
    elif period == "today":
        expense_records = get_expenses_for_today(expense_tracker_sheet)
    if expense_records:
        for expense in expense_records:
            print(
                f"Date: {expense['Date']}, "
                f"Name: {expense['Name']}, "
                f"Amount: €{expense['Amount']}, "
                f"Category: {expense['Category']}"
            )
    else:
        print("No expense found.")
    main()

def get_expenses_for_current_month(sheet): 
    """
    Allow the user to review the expenses logged in that particular month.
    """
    current_month = datetime.datetime.now().month
    expenses = sheet.get_all_records()
    return [expense for expense in expenses if expense['Date'].month == current_month]

def get_expenses_for_today(sheet):
    today = datetime.datetime.now().date()
    expenses = sheet.get_all_records()
    return [expense for expense in expenses if expense['Date'].date == today]


def calculate_total_expenses():
    """
    Allow user to calculate the total expenses over a specific period.
    This can help users understand their overall spending.
    """
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    expense_records = expense_tracker_sheet.get_all_records()
    total_expenses = sum(expense['Amount'] for expense in expense_records)
    print(f"Total Expenses: €{total_expenses}")
    main()


main()