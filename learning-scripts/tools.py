import faker
from langchain.tools import tool
fake = faker.Faker()

# will make simple tool that just purpose to make fake name - age - and address
@tool
def generate_fake_person() -> str:
    """Generate a fake person's name, age, and address."""
    name = fake.name()
    age = fake.random_int(min=18, max=90)
    address = fake.address().replace("\n", ", ")
    return f"Name: {name}, Age: {age}, Address: {address}"
