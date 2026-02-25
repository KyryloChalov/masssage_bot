from datetime import time
from include.business_info import BUSINESS_INFO
from models.business_model import Business


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
        print('business: ', business)

        if not business:
            raise ValueError("Business not found")

        return business
