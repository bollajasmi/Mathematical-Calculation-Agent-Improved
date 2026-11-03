import sympy as sp
import statistics
import ast
import math
import re
ALLOWED_OPERATORS = {
    ast.Add: lambda a, b: a + b,
    ast.Sub: lambda a, b: a - b,
    ast.Mult: lambda a, b: a * b,
    ast.Div: lambda a, b: a / b,
    ast.Pow: lambda a, b: a ** b,
}
ALLOWED_UNARY_OPERATORS = {
    ast.UAdd: lambda a: a,
    ast.USub: lambda a: -a,
}
ALLOWED_FUNCTIONS = {
    "sqrt": sp.sqrt,
    "sin": sp.sin,
    "cos": sp.cos,
    "tan": sp.tan,
    "asin": sp.asin,
    "acos": sp.acos,
    "atan": sp.atan,
    "log": sp.log,
    "exp": sp.exp,
    "factorial": sp.factorial,
    "abs": sp.Abs,
}
def evaluate_ast(node):
    # Handle numbers
    if isinstance(node, ast.Constant):
        if type(node.value) in (int, float):
            if type(node.value) is int and node.value.bit_length() > 1024:
                raise ValueError("Integer is too large.")

            if type(node.value) is float and not math.isfinite(node.value):
                raise ValueError("Invalid numeric value.")
            return sp.sympify(node.value)
        raise ValueError("Only numeric constants are allowed.")

    # Handle variables
    # Handle mathematical constants and variables
    if isinstance(node, ast.Name):
        if node.id == "pi":
            return sp.pi

        if node.id == "e":
            return sp.E

        return sp.Symbol(node.id)

    # Handle binary operations: +, -, *, /, **
    if isinstance(node, ast.BinOp):
        operator = type(node.op)

        if operator not in ALLOWED_OPERATORS:
            raise ValueError("Unsupported mathematical operator.")

        left = evaluate_ast(node.left)
        right = evaluate_ast(node.right)
        if operator == ast.Pow:
            if not right.is_number:
                raise ValueError("Exponent must be numeric.")

            if abs(right) > 1000:
                raise ValueError("Exponent is too large. Maximum absolute exponent is 1000.")

        return ALLOWED_OPERATORS[operator](left, right)

    # Handle unary operations: +5, -5
    if isinstance(node, ast.UnaryOp):
        operator = type(node.op)

        if operator not in ALLOWED_UNARY_OPERATORS:
            raise ValueError("Unsupported unary operator.")

        value = evaluate_ast(node.operand)

        return ALLOWED_UNARY_OPERATORS[operator](value)

    # Handle approved mathematical functions
    if isinstance(node, ast.Call):
        if not isinstance(node.func, ast.Name):
            raise ValueError("Unsupported function call.")

        function_name = node.func.id

        if function_name not in ALLOWED_FUNCTIONS:
            raise ValueError("Mathematical function not allowed.")

        if node.keywords:
            raise ValueError("Keyword arguments are not allowed.")

        arguments = [
            evaluate_ast(argument)
            for argument in node.args
        ]

        return ALLOWED_FUNCTIONS[function_name](*arguments)

    raise ValueError("Unsupported mathematical expression.")
def validate_ast_complexity(node):
    # Count the total number of AST nodes
    nodes = list(ast.walk(node))

    if len(nodes) > 100:
        raise ValueError("Expression is too complex. Maximum 100 nodes allowed.")

    # Calculate the maximum nesting depth
    def get_depth(current_node):
        child_depths = [
            get_depth(child)
            for child in ast.iter_child_nodes(current_node)
        ]

        return 1 + max(child_depths, default=0)

    if get_depth(node) > 20:
        raise ValueError("Expression is too deeply nested. Maximum depth is 20.")

def normalize_expression(expression):
    # Convert ^ into ** for powers
    expression = expression.replace("^", "**")

    # Add multiplication between a number and a variable: 5x -> 5*x
    expression = re.sub(r"(\d)([a-zA-Z])", r"\1*\2", expression)

    # Add multiplication between a number and parentheses: 3(x+2) -> 3*(x+2)
    expression = re.sub(r"(\d)\(", r"\1*(", expression)

    # Add multiplication between a variable and parentheses: x(x+2) -> x*(x+2)
    expression = re.sub(r"([a-zA-Z])\(", r"\1*(", expression)

    return expression

def safe_sympify(expression):
    if not isinstance(expression, str):
        raise TypeError("Expression must be a string.")

    expression = expression.strip()
    expression = normalize_expression(expression)

    if len(expression) > 500:
        raise ValueError("Expression is too long. Maximum 500 characters allowed.")

    try:
        parsed = ast.parse(expression, mode="eval")
    except SyntaxError:
        raise ValueError("Invalid mathematical expression.")
    validate_ast_complexity(parsed.body)

    return evaluate_ast(parsed.body)
def add(a, b):
    return a + b
def subtract(a, b):
    return a - b
def multiply(a, b):
    return a * b
def divide(a, b):
    if b == 0:
        raise ValueError("Cannot divide by zero.")
    return a / b
def power(base, exponent):
    return sp.Pow(base, exponent)
def square_root(number):
    if number < 0:
        raise ValueError("Cannot calculate a real square root of a negative number.")
    return sp.sqrt(number)
def factorial(number):
    if not isinstance(number, int) or number < 0:
        raise ValueError("Factorial requires a non-negative integer.")
    return sp.factorial(number)
def percentage(number, percent):
    return number * percent / 100
def simplify_expression(expression):
    return sp.simplify(safe_sympify(expression))
def expand_expression(expression):
    return sp.expand(safe_sympify(expression))
def factor_expression(expression):
    return sp.factor(safe_sympify(expression))
def solve_equation(equation, variable="x"):
    if equation.count("=") != 1:
        raise ValueError("Please provide an equation with exactly one '='.")

    left, right = equation.split("=")

    symbol = sp.Symbol(variable)

    equation = sp.Eq(
        safe_sympify(left),
        safe_sympify(right)
    )

    return sp.solve(equation, symbol)
def degrees_to_radians(angle):
    return angle * sp.pi / 180
def radians_to_degrees(angle):
    return angle * 180 / sp.pi
def sin_angle(angle):
    return sp.sin(degrees_to_radians(angle))
def cos_angle(angle):
    return sp.cos(degrees_to_radians(angle))
def tan_angle(angle):
    return sp.tan(degrees_to_radians(angle))
def sec_angle(angle):
    return 1 / cos_angle(angle)
def csc_angle(angle):
    return 1 / sin_angle(angle)
def cot_angle(angle):
    return 1 / tan_angle(angle)
def natural_log(number):
    return sp.log(number)
def common_log(number):
    return sp.log(number, 10)
def logarithm(number, base):
    if base <= 0 or base == 1:
        raise ValueError("Logarithm base must be positive and cannot be 1.")
    if number <= 0:
        raise ValueError("Logarithm input must be positive.")
    return sp.log(number, base)
def exponential(number):
    return sp.exp(number)
def differentiate_expression(expression, variable="x"):
    symbol = sp.Symbol(variable)
    expr = safe_sympify(expression)
    return sp.diff(expr, symbol)
def integrate_expression(expression, variable="x"):
    symbol = sp.Symbol(variable)
    expr = safe_sympify(expression)
    return sp.integrate(expr, symbol)
def calculate_limit(expression, variable="x", point=0):
    symbol = sp.Symbol(variable)
    expr = safe_sympify(expression)
    return sp.limit(expr, symbol, point)
def definite_integral(expression, variable="x", lower_limit=0, upper_limit=1):
    symbol = sp.Symbol(variable)
    expr = safe_sympify(expression)

    return sp.integrate(
        expr,
        (symbol, lower_limit, upper_limit)
    )
def solve_differential_equation(equation, function="y", variable="x"):
    x = sp.Symbol(variable)
    y = sp.Function(function)(x)

    left, right = equation.split("=")

    ode = sp.Eq(
        sp.sympify(left, locals={function: sp.Function(function)}),
        sp.sympify(right, locals={function: sp.Function(function)})
    )

    return sp.dsolve(ode, y)
def matrix_add(matrix_a, matrix_b):
    return sp.Matrix(matrix_a) + sp.Matrix(matrix_b)


def matrix_subtract(matrix_a, matrix_b):
    return sp.Matrix(matrix_a) - sp.Matrix(matrix_b)


def matrix_multiply(matrix_a, matrix_b):
    return sp.Matrix(matrix_a) * sp.Matrix(matrix_b)


def matrix_transpose(matrix):
    return sp.Matrix(matrix).T


def matrix_determinant(matrix):
    return sp.Matrix(matrix).det()


def matrix_inverse(matrix):
    mat = sp.Matrix(matrix)

    if mat.det() == 0:
        raise ValueError("A singular matrix has no inverse.")

    return mat.inv()
def solve_linear_system(equations, variables):
    symbols = sp.symbols(variables)

    sympy_equations = []

    for equation in equations:
        left, right = equation.split("=")

        sympy_equations.append(
            sp.Eq(
                safe_sympify(left),
                safe_sympify(right)
            )
        )

    return sp.solve(sympy_equations, symbols)
def calculate_mean(numbers):
    return statistics.mean(numbers)


def calculate_median(numbers):
    return statistics.median(numbers)


def calculate_mode(numbers):
    return statistics.multimode(numbers)


def calculate_variance(numbers):
    return statistics.variance(numbers)


def calculate_standard_deviation(numbers):
    return statistics.stdev(numbers)
def calculate_permutation(n, r):
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require 0 <= r <= n.")
    return sp.factorial(n) / sp.factorial(n - r)


def calculate_combination(n, r):
    if n < 0 or r < 0 or r > n:
        raise ValueError("Require 0 <= r <= n.")
    return sp.binomial(n, r)
def calculate_probability(favorable, total):
    if total <= 0 or favorable < 0 or favorable > total:
        raise ValueError("Invalid event counts.")
    return sp.Rational(favorable, total)


def complement_probability(probability):
    if not 0 <= probability <= 1:
        raise ValueError("Probability must be between 0 and 1.")
    return 1 - probability


def conditional_probability(joint_probability, given_probability):
    if not 0 <= joint_probability <= given_probability <= 1:
        raise ValueError("Invalid probability values.")
    if given_probability == 0:
        raise ValueError("Given event must have non-zero probability.")
    return joint_probability / given_probability


def independent_probability(probability_a, probability_b):
    if not (0 <= probability_a <= 1 and 0 <= probability_b <= 1):
        raise ValueError("Probabilities must be between 0 and 1.")
    return probability_a * probability_b