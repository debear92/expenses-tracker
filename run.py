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
            f"Expense: On {self.date} you have spent \
            €{self.amount} for {self.name}"
        )


def get_expense():
    """
    Get expense input from user.
    Convert the amounnt input to a float.
    Offer selected categories to choose from.
    """
    expense_date = input("Please enter your expense date (DD-MM-YYYY): \n")
    expense_name = input("Please, enter your expense name: \n")
    expense_amount = float(input("Please, enter your expense amount: \n"))
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
        chosen_index = int(
            input(f"Enter a category number {category_options}:")) - 1

        if chosen_index in range(len(expense_categories)):
            selected_category = expense_categories[chosen_index]
            new_expense = Expense(
                expense_date, expense_name, expense_amount, selected_category)

            return new_expense

        else:
            print("Invalid category. Please try again!")
        break


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


def view_expenses():
    """
    Allow user to view their previously recorded expenses.
    """
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    expense_records = expense_tracker_sheet.get_all_records()
    if expense_records:
        for expense in expense_records:
            print(
                f"Date: {expense['Date']}, Name: {expense['Name']}, \
                Amount: €{expense['Amount']}, Category: {expense['Category']}"
                )
    else:
        print("No expense found.")


def calculate_total_expenses():
    """
    Allow user to calculate the ttal expenses over a specific period.
    This can help users understand their overall spending.
    """
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    expense_records = expense_tracker_sheet.get_all_records()
    total_expenses = sum(expense['Amount'] for expense in expense_records)
    print(f"Total Expenses: €{total_expenses}")


def main():
    """
    Run program.
    """
    print("Welcome to the Ultimate Expense Tracker!")
    expense = get_expense()
    update_file(expense)


main()
