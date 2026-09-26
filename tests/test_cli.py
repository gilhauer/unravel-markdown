from pathlib import Path

from unravel.cli import main


def test_cli_generate_check_list_and_errors_are_concise(tmp_path, capsys):
    source = tmp_path / "source.md"
    source.write_text("```text <<nested/x.txt>>\nhello\n```\n", encoding="utf-8")
    output = tmp_path / "output"

    assert main([str(source), "-o", str(output)]) == 0
    assert "wrote" in capsys.readouterr().out
    assert main([str(source), "-o", str(output), "--check"]) == 0
    assert "current" in capsys.readouterr().out
    assert main([str(source), "--list"]) == 0
    assert "nested/x.txt [root]" in capsys.readouterr().out

    (output / "nested/x.txt").write_text("changed")
    assert main([str(source), "-o", str(output), "--check"]) == 1
    captured = capsys.readouterr()
    assert "changed" in captured.err or "modified" in captured.err
    assert "Traceback" not in captured.err


def test_python_module_and_console_parser_share_flags():
    # Both entry points call this same parser/main function; argparse rejects
    # incompatible read-only modes with its conventional exit status 2.
    try:
        main(["missing.md", "--list", "--check"])
    except SystemExit as exc:
        assert exc.code == 2
    else:
        raise AssertionError("argparse did not reject incompatible modes")
