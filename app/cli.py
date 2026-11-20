
from app.records import count_by, get_by_id, load_records, search

while True:
    print("\nJALSANCHAY MENU ")
    print("1. Display all records")
    print("2. Search records")
    print("3. Count records by category")
    print("4. Get record by ID")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        all_records = load_records()

        for i, record in enumerate(all_records, 1):
            print(f"\nID: {i}")
            print("Topic:", record["topic"])
            print("Section:", record["section"])
            print("Rule/Value:", record["rule_or_value"])

    elif choice == "2":
        keyword = input("Enter search keyword: ")
        results = search(keyword)

        if results:
            for record in results:
                print("\nTopic:", record["topic"])
                print("Rule/Value:", record["rule_or_value"])
        else:
            print("No matching records found.")

    elif choice == "3":
        category = input("Enter category field (topic, section, unit): ")
        counts = count_by(category)

        for name, total in counts.items():
            print(name, ":", total)

    elif choice == "4":
        record_id = int(input("Enter record ID (1-20): "))
        record = get_by_id(record_id)

        if record:
            print("\nTopic:", record["topic"])
            print("Section:", record["section"])
            print("Rule/Value:", record["rule_or_value"])
        else:
            print("Record not found.")

    elif choice == "0":
        print("Thank you for using JalSanchay!")
        break

    else:
        print("Invalid choice. Please try again.")
