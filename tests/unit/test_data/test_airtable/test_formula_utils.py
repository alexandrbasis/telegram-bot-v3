"""Tests for Airtable formula utility helpers."""

from src.data.airtable.formula_utils import escape_formula_value, prepare_formula_value
from src.models.participant import Role


class TestEscapeFormulaValue:
    """Test escaping behaviour for Airtable formulas."""

    def test_escape_single_quotes(self):
        assert escape_formula_value("O'Brien") == "O''Brien"

    def test_escape_multiple_quotes(self):
        assert escape_formula_value("'quoted'") == "''quoted''"

    def test_escape_without_quotes(self):
        assert escape_formula_value("PlainText") == "PlainText"


class TestPrepareFormulaValue:
    """Test normalization and quoting hints for Airtable formula values."""

    def test_prepare_handles_enum(self):
        should_quote, value = prepare_formula_value(Role.TEAM)
        assert should_quote is True
        assert value == "TEAM"

    def test_prepare_quotes_strings(self):
        should_quote, value = prepare_formula_value("O'Brien")
        assert should_quote is True
        assert value == "O''Brien"

    def test_prepare_passthrough_numbers(self):
        should_quote, value = prepare_formula_value(42)
        assert should_quote is False
        assert value == 42
