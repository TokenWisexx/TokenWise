import re
import math
import sympy
from sympy import sin, cos, tan, cot, sec, csc, sqrt, exp, log, pi, E, I, oo
from sympy.parsing.sympy_parser import parse_expr, standard_transformations, implicit_multiplication_application

# ── 1. MATH SOLVER (NUMERICAL & SYMBOLIC) ─────────────────────
MATH_TRIGGERS = [
    "calculate the value of", "calculate", "solve", "compute", "how much is", 
    "evaluate", "simplify", "what is the value of", "what is", "value of"
]

MATH_FUNCS = ["sin", "cos", "tan", "cot", "sec", "csc", "sqrt", "log", "ln", "exp", "abs", "factorial", "pi", "rad", "deg"]

def _preprocess_math_str(s):
    t = s.lower().strip()
    for trigger in MATH_TRIGGERS:
        if t.startswith(trigger + " "):
            t = t[len(trigger):].strip()
            break
        elif t.startswith(trigger) and len(t) > len(trigger) and t[len(trigger)] in " 0123456789(+-/*":
            t = t[len(trigger):].strip()
            break
    
    t = t.rstrip('?').strip()
    
    # Word-to-operator normalization
    t = t.replace("multiplied by", "*")
    t = t.replace("times", "*")
    t = t.replace("divided by", "/")
    t = t.replace("divided", "/")
    t = t.replace("plus", "+")
    t = t.replace("minus", "-")
    t = t.replace("to the power of", "**")
    t = t.replace("power of", "**")
    t = t.replace("squared", "**2")
    t = t.replace("cubed", "**3")
    t = t.replace("square root of", "sqrt")
    t = t.replace("cube root of", "cbrt")
    t = t.replace('^', '**').replace('×', '*').replace('÷', '/')
    
    # Fix shorthand like sinx -> sin(x), cosx -> cos(x), tanx -> tan(x)
    t = re.sub(r'\b(sin|cos|tan|cot|sec|csc|log|ln|sqrt)\s*([a-zA-Z0-9]+)\b', r'\1(\2)', t)
    # Fix ln -> log
    t = re.sub(r'\bln\(', 'log(', t)
    return t

def _is_math(text):
    t = text.lower().strip().rstrip('?')
    for trigger in MATH_TRIGGERS:
        if t.startswith(trigger + " "):
            t = t[len(trigger):].strip()
            break
        elif t.startswith(trigger) and len(t) > len(trigger) and t[len(trigger)] in " 0123456789(+-/*":
            t = t[len(trigger):].strip()
            break
    
    has_math_func = any(re.search(rf'\b{fn}\b|\b{fn}\(', t) for fn in MATH_FUNCS) or any(fn in t for fn in ["sinx", "cosx", "tanx", "cotx", "secx", "cscx"])
    has_digit = bool(re.search(r'\d', t))
    has_operator = bool(re.search(r'[\+\-\*\/\^\%\(\)\=]', t))
    has_word_op = any(w in t.split() for w in ["plus", "minus", "times", "divided", "squared", "cubed", "sqrt", "derivative", "integral", "factor"])

    # Must have either a distinct math function or digit with operator/word op
    if has_math_func:
        return True
    if has_digit and (has_operator or has_word_op):
        return True
    if has_word_op and (has_digit or any(c in t for c in "xyz")):
        return True

    return False

def _solve_math(text):
    t = _preprocess_math_str(text)
    if not t:
        return None

    # First try safe python eval for purely numeric expressions
    try:
        clean_arith = t.replace(' ', '')
        if re.match(r'^[\d\+\-\*\/\.\(\)\%\*\*]+$', clean_arith):
            val = eval(clean_arith, {"__builtins__": None}, {})
            if isinstance(val, (int, float)):
                if isinstance(val, float) and val.is_integer():
                    return str(int(val))
                return str(val)
    except Exception:
        pass

    transformations = (standard_transformations + (implicit_multiplication_application,))
    try:
        # Try symbolic simplification
        expr = parse_expr(t, transformations=transformations)
        
        # Don't treat a bare single symbol (e.g. 'brain', 'python') as a solved math expression
        if isinstance(expr, sympy.Symbol):
            return None
            
        simplified = sympy.simplify(expr)
        
        # If expression is numeric float/int
        if simplified.is_number:
            if simplified.is_Integer:
                return str(simplified)
            try:
                eval_val = float(simplified.evalf())
                if abs(eval_val - round(eval_val)) < 1e-9:
                    return f"{simplified} (= {int(round(eval_val))})"
                return f"{simplified} (≈ {round(eval_val, 4)})"
            except Exception:
                return str(simplified)
        
        # Symbolic result (e.g. sin(x)/cos(x) -> tan(x))
        if str(simplified) != t.strip():
            return str(simplified)
        return None
    except Exception:
        return None

# ── 2. GREETINGS ───────────────────────────────────────────────
GREETINGS = {
    "hi": "Hello! How can I help you today?",
    "hello": "Hi there! What can I do for you?",
    "hey": "Hey! How can I assist you?",
    "good morning": "Good morning! How can I help?",
    "good evening": "Good evening! What do you need?",
    "good afternoon": "Good afternoon! How can I help?",
    "thanks": "You're welcome! Let me know if you need anything else.",
    "thank you": "Happy to help! Feel free to ask more queries.",
    "bye": "Goodbye! Have a wonderful day!",
    "goodbye": "Goodbye! Take care!",
    "who are you": "I am Kuiper, an intelligent multi-layer AI router designed to optimize query execution and minimize LLM costs.",
}

def _is_greeting(text):
    t = text.lower().strip().rstrip('?!.')
    return t in GREETINGS or any(t == g or t.startswith(f"{g} ") for g in GREETINGS)

def _solve_greeting(text):
    t = text.lower().strip().rstrip('?!.')
    for g, response in GREETINGS.items():
        if t == g or t.startswith(f"{g} ") or t.startswith(g):
            return response
    return "Hello! How can I help you?"

# ── 3. UNIT CONVERSIONS ────────────────────────────────────────
CONVERSIONS = {
    # length
    ("cm", "meter"): (0.01, "1 meter = 100 cm"),
    ("meter", "cm"): (100, "1 meter = 100 cm"),
    ("km", "miles"): (0.621371, "1 km = 0.6214 miles"),
    ("miles", "km"): (1.60934, "1 mile = 1.6093 km"),
    ("feet", "meter"): (0.3048, "1 foot = 0.3048 meters"),
    ("meter", "feet"): (3.28084, "1 meter = 3.2808 feet"),
    ("inch", "cm"): (2.54, "1 inch = 2.54 cm"),
    ("cm", "inch"): (0.393701, "1 cm = 0.3937 inch"),
    # weight
    ("kg", "pounds"): (2.20462, "1 kg = 2.2046 lbs"),
    ("pounds", "kg"): (0.453592, "1 lb = 0.4536 kg"),
    ("grams", "oz"): (0.035274, "1 gram = 0.0353 oz"),
    # time
    ("hours", "minutes"): (60, "1 hour = 60 minutes"),
    ("minutes", "seconds"): (60, "1 minute = 60 seconds"),
    ("hours", "seconds"): (3600, "1 hour = 3,600 seconds"),
    ("days", "hours"): (24, "1 day = 24 hours"),
    ("days", "minutes"): (1440, "1 day = 1,440 minutes"),
    ("days", "seconds"): (86400, "1 day = 86,400 seconds"),
    ("weeks", "days"): (7, "1 week = 7 days"),
    ("weeks", "hours"): (168, "1 week = 168 hours"),
    # length extras
    ("km", "meter"): (1000, "1 km = 1,000 meters"),
    ("meter", "km"): (0.001, "1,000 meters = 1 km"),
    ("mm", "cm"): (0.1, "1 mm = 0.1 cm"),
    ("cm", "mm"): (10, "1 cm = 10 mm"),
}

def _is_conversion(text):
    t = text.lower()
    units = set(u for pair in CONVERSIONS.keys() for u in pair)
    return ("how many" in t or "convert" in t or " in " in t or " to " in t or "equals" in t) and \
           any(u in t for u in units)

def _solve_conversion(text):
    t = text.lower().replace("lbs", "pounds")
    for (from_unit, to_unit), (factor, explanation) in CONVERSIONS.items():
        if from_unit in t and to_unit in t:
            numbers = re.findall(r'\d+\.?\d*', t)
            if numbers:
                val = float(numbers[0])
                result = val * factor
                return f"{val} {from_unit} = {round(result, 4)} {to_unit} ({explanation})"
            return explanation
    return None

# ── 4. BASIC FACTS ─────────────────────────────────────────────
FACTS = {
    "what is pi":               f"π (pi) = {math.pi}",
    "what is euler":            f"e (Euler's number) = {math.e}",
    "speed of light":           "Speed of light in vacuum = 299,792,458 m/s (~3 × 10⁸ m/s)",
    "how many days in a year":  "365 days (366 days in a leap year)",
    "how many months in a year":"12 months",
    "how many weeks in a year": "52 weeks",
    "what is gravity":          "Standard gravitational acceleration on Earth (g) = 9.80665 m/s²",
    "boiling point of water":   "100°C (212°F / 373.15 K) at 1 atm",
    "freezing point of water":  "0°C (32°F / 273.15 K)",
    "how many seconds in a day":"86,400 seconds",
    "how many hours in a day":  "24 hours",
    "what is a byte":           "1 byte = 8 bits",
    "what is a kilobyte":       "1 KB = 1,024 bytes (or 1,000 bytes in SI decimal)",
    "what is a megabyte":       "1 MB = 1,024 KB = 1,048,576 bytes",
    "what is a gigabyte":       "1 GB = 1,024 MB = 1,073,741,824 bytes",
}

def _is_fact(text):
    t = text.lower().rstrip('?')
    return any(t == f or f in t for f in FACTS)

def _solve_fact(text):
    t = text.lower().rstrip('?')
    for fact, answer in FACTS.items():
        if fact in t:
            return answer
    return None

# ── MAIN HANDLER ───────────────────────────────────────────────
def handle(text):
    t = text.strip()

    # 1. Greetings
    if _is_greeting(t):
        return {"answer": _solve_greeting(t), "handled_by": "greeting", "pass_on": False}

    # 2. Basic Scientific/System Facts
    if _is_fact(t):
        ans = _solve_fact(t)
        if ans:
            return {"answer": ans, "handled_by": "facts", "pass_on": False}

    # 3. Unit Conversions
    if _is_conversion(t):
        ans = _solve_conversion(t)
        if ans:
            return {"answer": ans, "handled_by": "conversion", "pass_on": False}

    # 4. Numerical & Symbolic Math
    if _is_math(t):
        ans = _solve_math(t)
        if ans:
            return {"answer": f"= {ans}", "handled_by": "math", "pass_on": False}

    # Pass on to Layer 0B (General Knowledge)
    return {"answer": None, "handled_by": None, "pass_on": True}