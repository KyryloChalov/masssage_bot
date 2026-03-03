from datetime import time
from business.business_info import BUSINESS_INFO
from model.business import Business


class BusinessRepository:

    _businesses = {
        1: Business(
            id=1,
            name=BUSINESS_INFO["назва"],
            working_hours=(time(8, 0), time(23, 0)),
            allowed_locations=BUSINESS_INFO["міста"],
            services=BUSINESS_INFO["послуги"],
            price=BUSINESS_INFO["ціна"],
            phone=BUSINESS_INFO["телефон"],
        )
    }

    @classmethod
    def get(cls, business_id: int) -> Business:
        business = cls._businesses.get(business_id)

        if not business:
            raise ValueError("Business not found")

        print("business: ", business.name)
        print("phone:   ", business.phone)
        
        return business
