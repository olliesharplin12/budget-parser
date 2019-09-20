"""
Author: Ollie Sharplin
Created: 20/09/2019
TODO: Calculate Weekly Cost Only
TODO: Add category summary at top of csv with total weekly cost
"""

import csv
import sys

PATH_OF_CSV = "D:\\OneDrive\\Documents\\2019 Stuff\\Budget\\CSVs\\"
WRITE_PATH = "D:\\OneDrive\\Documents\\2019 Stuff\\Budget\\"

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
    
    def write_summary(self):
        """Formats a list of data to write to csv"""
        formatted_cost = "$" + str(round(self.cost, 2))

        return ["", self.date, self.description, formatted_cost]


class Category():
    """Class for each category of transactions which stores grouped transaction details"""

    def __init__(self, name):
        self.name = name
        self.transactions = []
    
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

        return round(total_cost, 2)
        
    def write_summary(self):
        """Prepares a list of category elements to be printed to csv"""
        total_cost = "$" + str(self.get_total_cost())

        return [self.name, total_cost]


def read(path):
    """Reads the data from the file into list of lines"""
    rows = []
    with open(path, 'r') as csvFile:
        reader = csv.reader(csvFile)
        rows = list(reader)
    csvFile.close()

    return list(rows)


def create_transactions(rows):
    """Turns a list of rows into a list of transaction instances"""
    transactions = []
    for row in rows:
        _, _, date, _, _, category_group, category, description, cost, income, _ = row
        transaction = Transaction(date, category_group, category, description, cost, income)
        transactions.append(transaction)
    
    return transactions


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


def prepare_write(categories):
    """Creates a list of rows which will be written to a csv file. Currenty data grouped by 
    categories with a list of transactions.
    """
    rows = []
    for category in categories:
        rows.append(category.write_summary())
        for transaction in category.transactions:
            rows.append(transaction.write_summary())
        rows.append([])
    
    return rows


def write_csv(file, rows):
    """Writes rows to a csv file"""
    with open(file, 'w', newline='') as writeFile:
        writer = csv.writer(writeFile)
        writer.writerows(rows)
    writeFile.close()


def main(filename):
    """Runs on program start, controls method calls"""
    read_file = PATH_OF_CSV + filename
    write_file = WRITE_PATH + filename
    rows = read(read_file)
    header = rows.pop(0)

    if (len(header) != 11):
        print("Incorrect format")
        sys.exit(1)

    transactions = create_transactions(rows)
    categories = create_categories(transactions)
    rows_to_write = prepare_write(categories)
    write_csv(write_file, rows_to_write)



main("20190920.csv")