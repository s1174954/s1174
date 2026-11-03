from prime import is_prime

def test_is_prime():
    assert is_prime(1) == False
    assert is_prime(2) == True
    assert is_prime(3) == True
    assert is_prime(4) == False
    assert is_prime(5) == True

if __name__ == "__main__":
    test_is_prime()
    print("All tests passed!")