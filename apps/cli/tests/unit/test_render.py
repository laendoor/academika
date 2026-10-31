from clika.render import render_result


def test_dict_a_tabla_campo_valor():
    assert render_result({"ok": True}) == "| campo | valor |\n| ----- | ----- |\n| ok    | True  |"


def test_lista_de_dicts_a_tabla_con_columnas():
    output = render_result([{"key": "smoke", "name": "Smoke"}, {"key": "m2", "name": "M2", "extra": 1}])
    lines = output.splitlines()
    assert lines[0] == "| key   | name  | extra |"
    assert lines[2] == "| smoke | Smoke |       |"
    assert lines[3] == "| m2    | M2    | 1     |"


def test_escalar_a_texto():
    assert render_result(42) == "42"


def test_lista_de_escalares_a_tabla_de_una_columna():
    output = render_result([1, "dos"])
    assert output.splitlines()[0] == "| valor |"
    assert "| dos   |" in output


def test_lista_vacia_no_imprime_tabla():
    assert render_result([]) == ""
