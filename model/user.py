class User:
    def __init__(self, first_name, last_name_father, last_name_mother, birth_date, phone_number, email, password, license=None):
        self.first_name = first_name
        self.last_name_father = last_name_father
        self.last_name_mother = last_name_mother
        self.birth_date = birth_date
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.license = license

    def __repr__(self):
        return f"User({self.first_name}, {self.last_name_father}, {self.last_name_mother}, {self.birth_date}, {self.phone_number}, {self.email})"
    
    def to_dict(self):
        """Returns a dictionary with the user's data."""
        return {
            "first_name": self.first_name,
            "last_name_father": self.last_name_father,
            "last_name_mother": self.last_name_mother,
            "birth_date": self.birth_date,
            "phone_number": self.phone_number,
            "email": self.email,
            "password": self.password,
            "license": self.license
        }

    @classmethod
    def from_dict(cls, data):
        """Creates an instance of User from a dictionary."""
        return cls(
            first_name=data.get('first_name'),
            last_name_father=data.get('last_name_father'),
            last_name_mother=data.get('last_name_mother'),
            birth_date=data.get('birth_date'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            password=data.get('password'),
            license=data.get('license')
        )
