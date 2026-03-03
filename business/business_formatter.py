
from business.business_info import BUSINESS_INFO
from business.sys_prompt import SYSTEM_PROMPT



def format_business_info(info: dict) -> str:
    return f"""
Назва: {info['назва']}
Регіон обслуговування: {info['регіон обслуговування']}
Райони області: {', '.join(info['райони Київської області'])}
Міста: {', '.join(info['міста'])}

Ціна: {info['ціна']}
Графік роботи: {info['години']}
Телефон: {info['телефон']}
Сайт: {info['сайт']}
Стать масажистів: {info['стать масажистів']}

Послуги: {', '.join(info['послуги'])}

Тривалість:
{chr(10).join(info['тривалість масажів'])}

Подарунковий сертифікат:
{info['подарунковий сертифікат']}
""".strip()



def build_system_context() -> list:
    business_block = format_business_info(BUSINESS_INFO)

    return [
        {"role": "system", "content": SYSTEM_PROMPT},
        {
            "role": "system",
            "content": f"ОФІЦІЙНІ ДАНІ ПРО СЕРВІС:\n{business_block}",
        },
    ]