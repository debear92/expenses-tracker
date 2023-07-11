import datetime
import calendar
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
EXPENSE_CATEGORIES = [
    "🍕 Food",
    "🏠 Home",
    "💼 Work",
    "💊 Health",
    "🎈 Misc"
]


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
            "Expense: "
            f"On {self.date} you have spent €{self.amount} for {self.name}"
        )


def manage_menus():
    """
    Display menus and handle user input for selecting options.
    """
    print("Welcome to the Ultimate Expense Tracker!")

    while True:
        print("What do you want to do today?")
        print("0. Instructions")
        print("1. Add a new expense.")
        print("2. View expenses")
        print("3. Calculate total expenses")
        print("4. Set budget")
        print("5. Calculate savings")
        print("6. Exit")

        option = input("Enter your choice:\n")
        if option == "0":
            get_help()
        if option == "1":
            expense = get_expense()
            update_file(expense)
        elif option == "2":
            view_expenses()
        elif option == "3":
            calculate_total_expenses()
        elif option == "4":
            month = input(
                "Enter the month (MM: 01, 02, ...):\n"
            )
            while not is_valid_month(month):
                month = input("Invalid month format."
                              "Please enter the month (MM: 01, 02, ...):\n")
            amount = float(input("Enter the budget amount:\n"))
            set_budget(month, amount)
        elif option == "5":
            month = input(
                "Enter the month (MM: 01, 02, ...):\n"
            )
            calculate_savings(month)
        elif option == "6":
            print("Thank you for using the Ultimate Expense Tracker! \n"
                  "Have a nice day!")
            exit()
        else:
            print("Invalid option. Please try again.")


def get_help():
    """
    Print instructions for optimal app usage.
    """
    print("1. Add a new expense: "
          "Select date, name, amount, category of your expense.")
    print("2. View expenses: "
          "Review all your expenses recorder or filter them "
          "either by category or date range.")
    print("3. Calculate total expenses: "
          "Check how much is your total spending for the month "
          "or for a certain category.")
    print("4. Set budget: "
          "Insert your spending goals for the month and challenge yourself.")
    print("5. Calculate savings: "
          "Check your leftover budget, compare your total spending "
          "for the month with the budget set.")
    option = input("Enter 6 if you wish to back to main menu:\n")
    if option == "6":
        manage_menus()
        return


def select_category():
    """
    Allow user to select a certain category for their expense.
    """
    while True:
        print("Select a category: ")
        for i, category_name in enumerate(EXPENSE_CATEGORIES):
            print(f"  {i + 1}.  {category_name}")
        category_options = f"[1 - {len(EXPENSE_CATEGORIES)}]"
        chosen_index = input(f"Enter a category number {category_options}:\n")
        try:
            chosen_index = int(chosen_index)
            if chosen_index in range(1, len(EXPENSE_CATEGORIES) + 1):
                selected_category = EXPENSE_CATEGORIES[chosen_index - 1]
                return selected_category
            else:
                print("Invalid category. Please try again!")
        except ValueError:
            print("Invalid input. Please enter a numeric value.")


def get_expense():
    """
    Get expense input from user.
    Convert the amount input to a float.
    Offer selected categories to choose from.
    """
    while True:
        expense_date = input("Please enter your expense date (DD/MM/YYYY):\n")
        if is_valid_date(expense_date):
            break
        else:
            print("Invalid date format. Please enter the date as DD/MM/YYYY.")

    expense_name = input("Please, enter your expense name:\n")

    while True:
        expense_amount = input("Please, enter your expense amount:\n")
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

    selected_category = select_category()
    new_expense = Expense(
        expense_date, expense_name,
        expense_amount, selected_category)
    return new_expense


def is_valid_date(date_string):
    """
    Check if a date string is valid and in the format DD/MM/YYYY.
    """
    try:
        datetime.datetime.strptime(date_string, "%d/%m/%Y")
        return True
    except ValueError:
        return False


def is_valid_month(month):
    """
    Check if the month string provided is valid and in the format MMM.
    Eg. Jan, Feb, Mar...
    """
    try:
        datetime.datetime.strptime(month, "%m")
        return True
    except ValueError:
        return False


def update_file(expense):
    """
    Update the google sheet with the data provided by the user.
    """
    print("Saving User Expense...")
    print(f"{expense}")

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
    print("User Expense saved successfully")


def view_expenses():
    """
    Allow the user to view their previously recorded expenses.
    Users can choose if to view all expenses logged,
    all the expenses for a chosen category
    or all the expenses for a certain timeframe.
    """
    print("What expenses would you like to view?")
    print("1. All expenses logged")
    print("2. This month's expenses")
    print("3. Today's expenses")
    print("4. Expenses by category")
    print("5. Go back to the main menu")
    choice = input("Enter your choice:\n")
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    if choice == "1":
        expense_records = expense_tracker_sheet.get_all_records()
    elif choice == "2":
        expense_records = get_expenses_for_current_month(expense_tracker_sheet)
    elif choice == "3":
        expense_records = get_expenses_for_today(expense_tracker_sheet)
    elif choice == "4":
        expense_records = get_expense_by_category()
    elif choice == "5":
        manage_menus()
        return
    else:
        print("Invalid timeframe selected. Please try again.")
        view_expenses()
        return

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
    view_expenses()


def get_expenses_for_current_month(sheet):
    """
    Allow the user to review the expenses logged in that particular month.
    """
    current_month = datetime.datetime.now().month
    expenses = sheet.get_all_records()
    return [
        expense
        for expense in expenses
        if datetime.datetime.strptime(
            expense['Date'], "%d/%m/%Y"
        ).month == current_month
    ]


def get_expenses_for_today(sheet):
    """
    Allow the user to review the expenses logged in that day.
    """
    today = datetime.datetime.now().date()
    expenses = sheet.get_all_records()
    return [
        expense
        for expense in expenses
        if datetime.datetime.strptime(
            expense['Date'], "%d/%m/%Y"
        ).date() == today
    ]


def get_expense_by_category():
    """
    Get the expenses for a specific category.
    """
    selected_category = select_category()
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    expenses = expense_tracker_sheet.get_all_records()
    expense_records = [
        expense
        for expense in expenses
        if expense['Category'] == selected_category
    ]
    return expense_records


def calculate_total_expenses():
    """
    Allow user to calculate the total expenses over a specific
    period or category.
    This can help users understand their overall spending.
    """
    expense_tracker_sheet = SHEET.worksheet("expenses_tracker")
    expense_records = expense_tracker_sheet.get_all_records()

    if not expense_records:
        print("No expenses found.")
        return
    print("Choose an option to calculate the total expenses:")
    print("1. Total expenses for all records")
    print("2. Total expenses for a specific category")
    print("3. Total expenses within a date range")
    option = input("Enter your choice:\n")

    if option == "1":
        total_expenses = sum(expense['Amount'] for expense in expense_records)
    elif option == "2":
        expense_records = get_expense_by_category()
        total_expenses = sum(
            expense['Amount'] for expense in expense_records
        )
    elif option == "3":
        while True:
            start_date = input("Enter the start date (DD/MM/YYYY):\n")
            if not is_valid_date(start_date):
                print(f"Invalid date: {start_date}. "
                      "Please enter the date as DD/MM/YYYY.")
            else:
                break
        while True:
            end_date = input("Enter the end date (DD/MM/YYYY):\n")
            if not is_valid_date(end_date):
                print(f"Invalid date: {end_date}. "
                      "Please enter the date as DD/MM/YYYY.")
            else:
                break
        is_valid_date(end_date)
        total_expenses = sum(
            expense['Amount'] for expense in expense_records
            if is_within_date_range(expense['Date'], start_date, end_date)
        )
    else:
        print("Invalid option selected.")
        return
    print(f"Total Expenses: {format_currency(total_expenses)}")


def is_within_date_range(date, start_date, end_date):
    """
    Check if a given date is within the specified date range
    """
    if not (is_valid_date(date) and
            is_valid_date(start_date) and
            is_valid_date(end_date)):
        return False
    date = datetime.datetime.strptime(date, "%d/%m/%Y").date()
    start_date = datetime.datetime.strptime(start_date, "%d/%m/%Y").date()
    end_date = datetime.datetime.strptime(end_date, "%d/%m/%Y").date()
    return start_date <= date <= end_date


def format_currency(amount):
    """
    Format the amount as currency with appropriate symbols and decimal places.
    """
    return "€{:.2f}".format(amount)


def set_budget(month, amount):
    """
    Allow users to set a specific budget in a specific month.
    """
    budget_sheet = SHEET.worksheet("budget")
    budget_sheet.append_row([month, amount])
    print(f"You have set a budget of €{amount} "
          f"for the month of {calendar.month_name[int(month)]}.")
    print("Budget sheet updated succesfully.")


def calculate_savings(month):
    """"
    Calculate the unspent amount for a specific month
    and moving to the saving sheet.
    """
    while not is_valid_month(month):
        month = input("Invalid month format. "
                      "Please enter the month (MM: 01, 02, ...):\n")

    # Ensure month is zero-padded (e.g., '07' instead of '7')
    month = month.zfill(2)
    budget_sheet = SHEET.worksheet("budget")
    expenses_sheet = SHEET.worksheet("expenses_tracker")
    savings_sheet = SHEET.worksheet("savings")
    budget_records = budget_sheet.get_all_records()
    expense_records = expenses_sheet.get_all_records()

    budget_amount = sum(
        record["Amount"]
        for record in budget_records
        if str(record["Month"]).zfill(2) == month
    )

    expense_amount = sum(
        record["Amount"]
        for record in expense_records
        if datetime.datetime.strptime(
            record["Date"], "%d/%m/%Y").strftime("%m") == month
    )

    unspent_amount = budget_amount - expense_amount

    if unspent_amount > 0:
        savings_sheet.append_row([month, unspent_amount])
        print("Your savings for the month of " +
              f"{calendar.month_name[int(month)]} are €{unspent_amount}")
        print("Saving sheet updated")
    else:
        spent_over_budget = abs(unspent_amount)
        print(f"You spent €{spent_over_budget} over the budget. "
              f"There are no savings for "
              f"the month of {calendar.month_name[int(month)]}."
              )


if __name__ == "__main__":
    manage_menus()