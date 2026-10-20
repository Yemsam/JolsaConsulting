import csv
import random

# Grouped to produce more culturally consistent name combinations.
names = {
    "Yoruba": {
        "first": [
            "Adeola", "Oluwaseun", "Babatunde", "Yetunde", "Temitope",
            "Olamide", "Folake", "Adebayo", "Abimbola", "Oluwatobi"
        ],
        "last": [
            "Adeyemi", "Adebayo", "Ogunleye", "Olawale", "Akinola",
            "Balogun", "Adesina", "Ojo", "Ajayi", "Adeleke"
        ]
    },
    "Igbo": {
        "first": [
            "Chinedu", "Ngozi", "Ifeanyi", "Chiamaka", "Emeka",
            "Nneka", "Obinna", "Adaeze", "Uche", "Chidinma"
        ],
        "last": [
            "Okafor", "Okeke", "Eze", "Nwosu", "Obi",
            "Nwachukwu", "Onyeka", "Okonkwo", "Umeh", "Nnamani"
        ]
    },
    "Hausa": {
        "first": [
            "Musa", "Aisha", "Ibrahim", "Fatima", "Abdullahi",
            "Zainab", "Sani", "Hauwa", "Usman", "Aminu"
        ],
        "last": [
            "Bello", "Abubakar", "Suleiman", "Yusuf", "Aliyu",
            "Garba", "Ibrahim", "Umar", "Adamu", "Lawal"
        ]
    }
}

# Nigerian mobile prefixes in local format.
prefixes = ["0803", "0806", "0703", "0813", "0805", "0802", "0809"]
used_phones = set()

with open("nigerian_test_data.csv", "w", newline="", encoding="utf-8-sig") as file:
    writer = csv.writer(file)
    writer.writerow(["id", "first_name", "last_name", "phone", "email"])

    for person_id in range(1, 1001):
        group = random.choice(list(names.values()))
        first = random.choice(group["first"])
        last = random.choice(group["last"])

        while True:
            local_phone = random.choice(prefixes) + f"{random.randrange(10_000_000):07d}"
            phone = "+234" + local_phone[1:]
            if phone not in used_phones:
                used_phones.add(phone)
                break

        email = f"{first}.{last}.{person_id}@example.com".lower()
        writer.writerow([person_id, first, last, phone, email])

print("Created nigerian_test_data.csv with 1,000 records.")