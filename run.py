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
    def __init__(self, name, amount, category):
        self.name = name
        self.amount = amount
        self.category = category


def get_expense():
    """
    Get expense input from user.
    Convert the amounnt input to a float.
    Offer selected categories to choose from.
    """
    print("Welcome to the Ultimate Expense Tracker!")
    expense_name = input("Please, enter your expense name: \n")
    expense_amount = float(input("Please, enter your expense amount: \n"))
    print(f"You have entered {expense_name}, {expense_amount}")

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
        chosen_index = int(input(f"Enter a category number {category_options}:")) - 1

        if chosen_index in range(len(expense_categories)):
            break
        else:
            print("Invalid category. Please try again!")
  
        break


get_expense()
