class User:
    def __init__(self, first_name, last_name_father, last_name_mother, birth_date, phone_number, email, password, license=None, profilePictureUrl=None):
        default_profile_picture_url = "https://st.depositphotos.com/1537427/3571/v/450/depositphotos_35717211-stock-illustration-vector-user-icon.jpg"
        self.first_name = first_name
        self.last_name_father = last_name_father
        self.last_name_mother = last_name_mother
        self.birth_date = birth_date
        self.phone_number = phone_number
        self.email = email
        self.password = password
        self.license = license
        self.profilePictureUrl = profilePictureUrl or default_profile_picture_url

    def __repr__(self):
        return (f"User({self.first_name}, {self.last_name_father}, {self.last_name_mother}, "
                f"{self.birth_date}, {self.phone_number}, {self.email}, {self.profilePictureUrl})")

    def to_dict(self):
        """Devuelve un diccionario con los datos del usuario."""
        return {
            "first_name": self.first_name,
            "last_name_father": self.last_name_father,
            "last_name_mother": self.last_name_mother,
            "birth_date": self.birth_date,
            "phone_number": self.phone_number,
            "email": self.email,
            "password": self.password,
            "license": self.license,
            "profilePictureUrl": self.profilePictureUrl
        }

    @classmethod
    def from_dict(cls, data):
        """Crea una instancia de User a partir de un diccionario."""
        return cls(
            first_name=data.get('first_name'),
            last_name_father=data.get('last_name_father'),
            last_name_mother=data.get('last_name_mother'),
            birth_date=data.get('birth_date'),
            phone_number=data.get('phone_number'),
            email=data.get('email'),
            password=data.get('password'),
            license=data.get('license'),
            profilePictureUrl=data.get('profilePictureUrl')
        )
