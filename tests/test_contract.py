import importlib.resources

import urlsyntax

PUBLIC_API: list[str] = ["is_valid_http_url", "normalize"]


def test_all_lists_exactly_the_public_api() -> None:
    assert sorted(urlsyntax.__all__) == sorted(PUBLIC_API)


def test_every_exported_name_resolves() -> None:
    for name in urlsyntax.__all__:
        assert hasattr(urlsyntax, name)


def test_version_is_a_three_part_string() -> None:
    parts = urlsyntax.__version__.split(".")
    assert len(parts) == 3
    assert all(part.isdigit() for part in parts)


def test_the_package_ships_type_information() -> None:
    assert importlib.resources.files("urlsyntax").joinpath("py.typed").is_file()
