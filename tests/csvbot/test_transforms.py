"""
test/csvbot/test_transforms.py
"""


from src.csvbot.transforms import digits_only, currency_to_minor


def test_digits_only():
    assert digits_only("a1b2c3") == "123"

def test_currency_to_minor():
    assert currency_to_minor("12.34") == "1234"
    assert currency_to_minor("12") == "1200"