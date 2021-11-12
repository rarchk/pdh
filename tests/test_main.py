import io
from rich.console import Console
from pdh import main
from click import testing
import pkg_resources


def test_assert_true():
    assert True


def test_main_cli():
    runner = testing.CliRunner()
    assert runner.invoke(main.main, "").exit_code == 0


def test_main_version():
    runner = testing.CliRunner()
    result = runner.invoke(main.main, "version")
    assert result.exit_code == 0
    assert result.stdout == f"v{pkg_resources.get_distribution('pdh').version}\n"


def test_print_items_table():
    items = [{"Title": "text", "Url": "https://localhost"}]
    expected = "┏━━━━━━━┳━━━━━━━━━━━━━━━━━━━┓\n┃ Title ┃ Url               ┃\n┡━━━━━━━╇━━━━━━━━━━━━━━━━━━━┩\n│ text  │ https://localhost │\n└───────┴───────────────────┘\n"
    console = Console(force_terminal=True, file=io.StringIO(), _environ={}, color_system=None)
    main.print_items(items, output="table", skip_columns=[], plain_print_f=None, console=console)
    assert console.file.getvalue() == expected


def test_print_items_yaml():
    items = [{"Title": "text", "Url": "https://localhost"}]
    expected = "- Title: text\n  Url: https://localhost\n\n"
    console = Console(force_terminal=True, file=io.StringIO(), _environ={}, color_system=None)
    main.print_items(items, output="yaml", console=console)
    assert console.file.getvalue() == expected


def test_print_items_json():
    items = [{"Title": "text", "Url": "https://localhost"}]
    expected = '[{"Title": "text", "Url": "https://localhost"}]\n'
    console = Console(force_terminal=True, file=io.StringIO(), _environ={}, color_system=None)
    main.print_items(items, output="json", console=console)
    assert console.file.getvalue() == expected


def test_print_items_raw():
    items = [{"Title": "text", "Url": "https://localhost"}]
    expected = "[{'Title': 'text', 'Url': 'https://localhost'}]\n"
    console = Console(force_terminal=True, file=io.StringIO(), _environ={}, color_system=None)
    main.print_items(items, output="raw", console=console)
    assert console.file.getvalue() == expected


def test_print_items_plain():
    items = [{"Title": "text", "Url": "https://localhost"}]
    expected = "{'Title': 'text', 'Url': 'https://localhost'}\n"
    console = Console(force_terminal=True, file=io.StringIO(), _environ={}, color_system=None)
    main.print_items(items, output="plain", console=console)
    assert console.file.getvalue() == expected
