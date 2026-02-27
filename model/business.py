class Business:
    def __init__(
        self,
        id: int,
        name: str,
        working_hours: tuple,
        allowed_locations: list,
        services: list,
        price: str,
        phone: str,
    ):
        self.id = id
        self.name = name
        self.working_hours = working_hours
        self.allowed_locations = allowed_locations
        self.services = services
        self.price = price
        self.phone = phone
