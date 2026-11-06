while True:
    print("\n JALSANCHAY MENU ")
    print("1. About JalSanchay")
    print("2. Sample Questions")
    print("3. Rainwater Harvesting Rule Check")
    print("0. Exit")

    choice = input("Enter your choice: ")

    if choice == "1":
        print("\nJalSanchay helps design rooftop rainwater harvesting")
        print("and groundwater recharge systems using CGWB manuals.")

    elif choice == "2":
        print("\nSample Questions:")
        print("1. How much rainwater can a rooftop collect?")
        print("2. What is the purpose of a first-flush system?")
        print("3. How do I estimate rainwater storage capacity?")

    elif choice == "3":
        rainfall = float(input("Enter annual rainfall in mm: "))

        if rainfall >= 500:
            print("Rainwater harvesting may be a suitable option.")
        else:
            print("Rainfall is relatively low. Evaluate feasibility carefully.")

    elif choice == "0":
        print("Thank you for using JalSanchay!")
        break

    else:
        print("Invalid choice. Please select 1, 2, 3 or 0.")
