"""Strict interpreter for the contract scripts' tiny subset, NOT Clausewitz.

Tests execute the shipped .txt effects instead of an independent Python model.
Scope semantics, engine loading, GUI and pulse scheduling still need game tests.
"""
from decimal import Decimal
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
TOKEN = re.compile(r'\s+|\#[^\n]*|"(?:\\.|[^"\\])*"|>=|<=|!=|[{}=<>]|[^\s{}=<>!"#]+')


def parse(text):
    tokens, end = [], 0
    for match in TOKEN.finditer(text):
        if match.start() != end:
            raise ValueError(f"Invalid token at {end}")
        end = match.end()
        item = match.group()
        if not item.isspace() and not item.startswith("#"):
            tokens.append(item)
    if end != len(text):
        raise ValueError("Unparsed trailing text")
    position = 0

    def block(nested=False):
        nonlocal position
        nodes = []
        while position < len(tokens):
            if tokens[position] == "}":
                if not nested:
                    raise ValueError("Unexpected closing brace")
                position += 1
                return nodes
            key = tokens[position]
            position += 1
            if position + 1 >= len(tokens):
                raise ValueError(f"Incomplete assignment: {key}")
            op = tokens[position]
            position += 1
            if op not in ("=", ">", "<", ">=", "<=", "!="):
                raise ValueError(f"Invalid operator {op}")
            value = tokens[position]
            position += 1
            if value == "{":
                value = block(True)
            elif value in ("}", "=", ">", "<"):
                raise ValueError(f"Missing value for {key}")
            elif value.startswith('"'):
                value = value[1:-1]
            nodes.append((key, op, value))
        if nested:
            raise ValueError("Missing closing brace")
        return nodes
    return block()


def definitions(folder):
    result = {}
    for path in sorted((ROOT / "mod/common" / folder).glob("*.txt")):
        for name, op, value in parse(path.read_text(encoding="utf-8-sig")):
            if name in result or op != "=":
                raise ValueError(f"Duplicate/invalid definition {name}")
            result[name] = value
    return result


class Runtime:
    def __init__(self, treasury="1000000"):
        self.variables = {}
        self.treasury = Decimal(treasury)
        self.effects = definitions("scripted_effects")
        self.triggers = definitions("scripted_triggers")
        self.values = definitions("script_values")
        self.buttons = definitions("scripted_buttons")

    def value(self, item):
        if isinstance(item, list):
            result = Decimal(0)
            prior = False
            for key, _, operand in item:
                if key in ("if", "else_if", "else"):
                    fields = dict((k, v) for k, _, v in operand)
                    eligible = key == "if" or not prior
                    matched = eligible and (key == "else" or self.condition(fields["limit"]))
                    if key == "if":
                        prior = False
                    if matched:
                        result = self.apply_math(result, [(k, op, v) for k, op, v in operand if k != "limit"])
                        prior = True
                else:
                    result = self.apply_math(result, [(key, "=", operand)])
            return result
        if item in ("yes", "no"):
            return item == "yes"
        if item.startswith("var:"):
            return self.variables[item[4:]]
        if item == "gold_reserves":
            return self.treasury
        if item in self.values:
            return self.value(self.values[item])
        return Decimal(item)

    def apply_math(self, current, nodes):
        for key, _, operand in nodes:
            value = self.value(operand)
            if key == "value": current = value
            elif key == "add": current += value
            elif key == "subtract": current -= value
            elif key == "multiply": current *= value
            elif key == "divide": current /= value
            else: raise ValueError(f"Unsupported math {key}")
        return current

    def condition(self, nodes):
        def check(key, op, operand):
            if key in ("AND", "OR", "NOT"):
                tests = (check(k, o, v) for k, o, v in operand)
                if key == "OR": return any(tests)
                if key == "NOT": return not all(tests)
                return all(tests)
            if key == "always": return operand == "yes"
            if key == "is_player": return operand == "yes"
            if key == "has_variable": return operand in self.variables
            if key in self.triggers:
                result = self.condition(self.triggers[key])
                return result if operand == "yes" else not result
            if key.startswith("var:") and key[4:] not in self.variables:
                return False
            left, right = self.value(key), self.value(operand)
            if op == "=": return left == right
            if op == "!=": return left != right
            if op == ">": return left > right
            if op == "<": return left < right
            if op == ">=": return left >= right
            if op == "<=": return left <= right
            raise ValueError(f"Unsupported condition {key} {op}")
        return all(check(k, o, v) for k, o, v in nodes)

    def execute(self, nodes):
        prior = False
        for key, _, operand in nodes:
            if key in ("if", "else_if", "else"):
                fields = dict((k, v) for k, _, v in operand)
                eligible = key == "if" or not prior
                matched = eligible and (key == "else" or self.condition(fields["limit"]))
                if key == "if": prior = False
                if matched:
                    self.execute([(k, op, v) for k, op, v in operand if k != "limit"])
                    prior = True
            elif key == "set_variable":
                fields = dict((k, v) for k, _, v in operand)
                self.variables[fields["name"]] = self.value(fields["value"])
            elif key == "remove_variable":
                self.variables.pop(operand, None)
            elif key == "change_variable":
                fields = dict((k, v) for k, _, v in operand)
                name = fields.pop("name")
                self.variables[name] = self.apply_math(self.variables[name], [(k, "=", v) for k, v in fields.items()])
            elif key == "add_treasury":
                self.treasury += self.value(operand)
            elif key in self.effects:
                self.call(key)
            else:
                raise ValueError(f"Unsupported effect {key}")

    def call(self, name):
        self.execute(self.effects[name])

    def click(self, name):
        fields = dict((k, v) for k, _, v in self.buttons[name])
        if self.condition(fields["possible"]):
            self.execute(fields["effect"])
            return True
        return False

    def tick(self, count=1):
        for _ in range(count):
            self.call("mc_weekly_tick")
