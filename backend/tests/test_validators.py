from app.ingest.validators import validate_btc_address, validate_evm_address, validate_tron_address


def test_valid_tron():
    assert validate_tron_address("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
    assert validate_tron_address("TN7Wkr2xCJN83VCcURkAPAAAKn9gZxrQDE")

def test_invalid_tron():
    assert not validate_tron_address("0x1234567890abcdef1234567890abcdef12345678")
    assert not validate_tron_address("T" + "x" * 10)  # too short
    assert not validate_tron_address("")
    assert not validate_tron_address("A" + "1" * 33)  # wrong prefix

def test_valid_evm():
    assert validate_evm_address("0xdac17f958d2ee523a2206206994597c13d831ec7")
    assert validate_evm_address("0xDAC17F958D2EE523A2206206994597C13D831EC7")

def test_invalid_evm():
    assert not validate_evm_address("0x123")  # too short
    assert not validate_evm_address("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
    assert not validate_evm_address("")
    assert not validate_evm_address("dac17f958d2ee523a2206206994597c13d831ec7")  # no 0x

def test_valid_btc():
    assert validate_btc_address("1A1zP1eP5QGefi2DMPTfTL5SLmv7DivfNa")
    assert validate_btc_address("3J98t1WpEZ73CNmQviecrnyiWrnqRhWNLy")
    assert validate_btc_address("bc1qw508d6qejxtdg4y5r3zarvary0c5xw7kv8f3t4")

def test_invalid_btc():
    assert not validate_btc_address("0x1234567890abcdef")
    assert not validate_btc_address("")
    assert not validate_btc_address("TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t")
