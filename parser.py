"""
Author: Ollie Sharplin
Created: 20/09/2019
TODO: Check for arguments or add file name input from user
TODO: Implement multiple file analysis for weeks with month change
"""

import csv
import sys
import locale
locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
from datetime import datetime
from datetime import timedelta

PATH_OF_CSV = "D:\\OneDrive\\Documents\\2019 Stuff\\Budget\\CSVs\\"
WRITE_PATH = "D:\\OneDrive\\Documents\\2019 Stuff\\Budget\\"
FIRST_DAY_OF_WEEK = 1    # Monday=0, Sunday=6
DATE_FORMAT = "%d/%m/%Y"


class Transaction():
    """Class which stores all details regarding a single transaction"""

    def __init__(self, date, category_group, category, description, cost, income):
        self.date = date
        self.category_group = category_group
        self.category = category
        self.description = description
        
        if (income != "$0.00"):
            self.cost = float(income[1:]) * -1
            self.category = "Income"
        else:
            self.cost = float(cost[1:])
    
    def __lt__(self, other):
        """Built in less than method for comparing transactions by date and then name"""
        if (self.date != other.date):
            return self.date > other.date
        else:
            return self.description < other.description
    
    def write_summary(self):
        """Formats a list of data to write to csv"""
        formatted_cost = format_currency(self.cost)

        return ["", self.date, self.description, formatted_cost]


class Week():
    """Stores transactions by week"""

    def __init__(self, start_date):
        self.start_date = start_date
        self.end_date = start_date + timedelta(days=6)
        self.transactions = []
    
    def add_transaction(self, transaction):
        """Adds a transaction to the transaction list, transaction must be an instance of 
        Transaction class and date must be within date range of week. Returns 0 on success or -1 on 
        error.
        """
        if (isinstance(transaction, Transaction) and self.in_week(transaction.date)):
            self.transactions.append(transaction)
            return 0
        else:
            print("Transaction failed to add")
            return -1
    
    def in_week(self, date):
        """Checks if the supplied date is within the week, returns true if it is."""
        return date >= self.start_date and date <= self.end_date
    
    def get_total_spent(self, include_rent=False):
        """Calculates and retrieves the total amount spent for the week. Does not include income. 
        Formats with $ and rounds to 2dp. If include_rent is set to true, rent amount is included in 
        sum.
        """
        total_spent = 0
        for transaction in self.transactions:
            if (transaction.cost > 0 and (transaction.category != "Rent" or include_rent)):
                total_spent += transaction.cost
        
        formatted_amount = format_currency(total_spent)
        return formatted_amount


class Category():
    """Class for each category of transactions which stores grouped transaction details"""

    def __init__(self, name):
        self.name = name
        self.transactions = []
    
    def __lt__(self, other):
        """Defines a comparator for categories based on total cost, then number of transactions, 
        then name.
        """
        if (self.get_total_cost() != other.get_total_cost()):
            return self.get_total_cost() > other.get_total_cost()
        elif (len(self.transactions) != len(other.transactions)):
            return len(self.transactions) > len(other.transactions)
        else:
            return self.name < other.name
    
    def add_transaction(self, transaction):
        """Adds a transaction to the transaction list, transaction must be an instance of 
        Transaction class and categories must match. Returns 0 on success or -1 on error.
        """
        if (isinstance(transaction, Transaction) and transaction.category == self.name):
            self.transactions.append(transaction)
            return 0
        else:
            print("Transaction failed to add")
            return -1
    
    def get_total_cost(self):
        """Calculates and returns the total cost of all transactions rounded to 2dp with $ header"""
        total_cost = 0
        for transaction in self.transactions:
            total_cost += transaction.cost

        return total_cost
        
    def write_summary(self):
        """Prepares a list of category elements to be printed to csv"""
        total_cost = format_currency(self.get_total_cost())

        return [self.name, total_cost]


def format_currency(number):
    """Formats a number to 2dp with a leading $"""
    abs_number = abs(number)
    num_str = locale.currency(abs_number, grouping=True)
    
    if (number < 0):
        num_str = "-" + num_str
    
    return num_str


def read(filename):
    """Reads the data from the file into list of lines"""
    file = PATH_OF_CSV + filename
    rows = []
    with open(file, 'r') as csvFile:
        reader = csv.reader(csvFile)
        rows = list(reader)
    csvFile.close()

    return list(rows)


def create_transactions(rows):
    """Turns a list of rows into a list of transaction instances"""
    transactions = []
    for row in rows:
        _, _, date_str, _, _, category_group, category, description, cost, income, _ = row
        date = datetime.strptime(date_str, DATE_FORMAT).date()
        transaction = Transaction(date, category_group, category, description, cost, income)
        transactions.append(transaction)
    
    return transactions


def seperate_by_week(transactions):
    """Groups transactions by week discarding the first and last transactions which do not represent
    a full week.
    """
    transactions.sort()
    weeks = []

    if (len(transactions) > 0):
        first_date = transactions[-1].date
        while (first_date.weekday() != FIRST_DAY_OF_WEEK):
            first_date -= timedelta(days=1)    # TODO: Change to +=

        last_date = transactions[0].date
        while (last_date.weekday() != FIRST_DAY_OF_WEEK - 1 % 7):
            last_date += timedelta(days=1)    # TODO: Change to -=
        
        date = first_date
        while (date < last_date):
            new_week = Week(date)
            weeks.append(new_week)
            date += timedelta(days=7)
        
        for transaction in transactions:
            for week in weeks:
                if (week.in_week(transaction.date)):
                    week.add_transaction(transaction)
                    break

    return weeks


def create_categories(transactions):
    """Turns a list of transactions into a list of categories containing transaction details"""
    categories = []

    for transaction in transactions:
        category_found = False
        for category in categories:
            if (transaction.category == category.name):
                category.add_transaction(transaction)
                category_found = True
        
        if (not category_found):
            category = Category(transaction.category)
            category.add_transaction(transaction)
            categories.append(category)
    
    return categories


def prepare_write(week, categories):
    """Creates a list of rows which will be written to a csv file. Currenty data grouped by 
    categories with a list of transactions.
    """
    categories.sort()

    # Prepares header
    rows = [["Weekly Budget", week.start_date.strftime("%d %b") + " - " + week.end_date.strftime("%d %b")], []]

    # Prepares summary table
    for category in categories:
        rows.append(category.write_summary())

    total_spent = week.get_total_spent()
    total_including_rent = week.get_total_spent(True)

    rows.extend([[], ["Total Spent:", total_spent]])

    if (total_spent != total_including_rent):
        rows.append(["Including Rent:", total_including_rent])
    
    rows.extend([[], []])

    # Prepares transaction details per category
    rows.extend([["Category", "Date", "Description", "Amount"], []])

    for category in categories:
        rows.append([category.name + " ({})".format(format_currency(category.get_total_cost()))])
        for transaction in category.transactions:
            rows.append(transaction.write_summary())

        rows.append([])
    
    return rows


def write_csv(week, rows):
    """Writes rows to a csv file"""
    filename = week.start_date.strftime("%Y%m%d") + ".csv"
    file = WRITE_PATH + filename

    try:
        with open(file, 'w', newline='') as writeFile:
            writer = csv.writer(writeFile)
            writer.writerows(rows)
        writeFile.close()
    except PermissionError:
        print("File {} is open or is not in a location with write permissions".format(filename))


def main(filename):
    """Runs on program start, controls method calls"""
    rows = read(filename)
    header = rows.pop(0)

    if (len(header) != 11):
        print("Incorrect format")
        sys.exit(1)

    transactions = create_transactions(rows)
    weeks = seperate_by_week(transactions)

    for week in weeks:
        categories = create_categories(week.transactions)
        rows_to_write = prepare_write(week, categories)
        write_csv(week, rows_to_write)



main("20190921.csv")