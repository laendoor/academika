from analytika.utils.numeros import nota_numerica, porcentaje, promedio


def test_nota_numerica():
    assert nota_numerica("7") == 7
    assert nota_numerica(" 10 ") == 10
    assert nota_numerica("A") is None
    assert nota_numerica("PA") is None
    assert nota_numerica(None) is None


def test_promedio():
    assert promedio([8, 9]) == 8.5
    assert promedio([1, 2]) == 1.5
    assert promedio([]) is None


def test_porcentaje():
    assert porcentaje(1, 4) == 25.0
    assert porcentaje(20, 52) == 38.5
    assert porcentaje(0, 0) is None
