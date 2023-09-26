from src.schemas.dmail_profile import DmailProfileSchema

from faker import Faker


def generate_random_profile() -> DmailProfileSchema:
    """
    Generate random profile for dmail
    :return:
    """
    fake = Faker()
    profile = fake.profile()
    email_address = profile['mail']
    theme_raw = fake.company()
    theme = theme_raw if len(theme_raw) <= 31 else theme_raw[:31]

    return DmailProfileSchema(
        email=email_address,
        theme=theme.title()
    )
