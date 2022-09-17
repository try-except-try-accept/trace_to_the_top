
from config import *

import inspect

from flask import g

g._namespace = "__main__()"
g.exec_q = []
g.trace_table = {}

###################################################################################################

def record_namespace(out: list, indent: str, _params: str = "()"):
    '''Make a function take note of its namespace'''
    out.append(indent + "_this_func = inspect.stack()[0][3]")

    out.append(indent + '_namespace = f"{_this_func}' + _params + '"')
    out.append(indent + "print(_namespace, 'is my namespace')")
    out.append(indent + "log_locals(locals(), _namespace)")


def add_new_line_trigger(out: list, indent: str):
    out.append(indent + "NL_TRIGGER = True")  # force new line in trace table
    out.append(indent + "log_locals(locals(), _namespace)")
    out.append(indent + "NL_TRIGGER = False")
    out.append(indent + "del NL_TRIGGER")
###################################################################################################

def get_trace_table(code: str) -> str:
    '''Iterate through some program code and allow the program to annotate its memory changes
    to create a trace table. Include logical expressions and output statements as well as variable values.
    RETURNS: string - a new version of the code with the annotation enabled'''

    out = []
    new_line_trigger = False

    for_loop_stack = []

    for i, line in enumerate(code.split("\n")):
        s_line = line.strip()
        if not s_line:    continue                                               # skip blank lines

        indent = get_indent(line)

        if i == 0:
            record_namespace(out, indent)

        _this_func = inspect.stack()[0][3]

        if s_line.startswith("def "):

            _params = s_line.split("(")[1][:-2]

            if not _params:
                _params = '()'
            else:
                for delim in ":=":                                                  # handle type hints and kwargs
                    _params = "^%".join(p.split(delim)[0]
                                  for p in _params.replace(" ", "").split(","))
                _params = "(" + _params + ")"

            out.append(line)
            indent += SPACE4
            record_namespace(out, indent, _params)

        elif s_line.startswith("for "):
            out.append(line)
            indent += SPACE4
            add_new_line_trigger(out, indent)

            out.append(indent + "log_locals(locals(), _namespace)")

        elif (if_found := "if " in s_line[:5]) or \
             (while_found := s_line.startswith("while ")):                            # ensure logic exps are recorded
            kw = "if " if if_found else "while "
            cond = s_line.split(kw)[1][:-1]                                          # despace condition to allow var name and
            cond = {convert_to_var(cond):f"$%eval('{cond}')$%"}                      # set up the logic exp to evaluate later
            line = line.replace(kw,
                                f"{kw}log_locals(locals(), _namespace, {cond}) and ") # include memory lookup in condition
            out.append(line)

        elif (return_found := s_line.startswith("return ")) or \
             (print_found := s_line.startswith("print(")):
            kw = "return " if return_found else "print("                             # track print() and return too
            _, output = s_line.split(kw)
            if kw == "print(":
                output = output[:-1]                                                 # get rid of last bracket
                kw = kw[:-1]

            out.append(indent + f"{kw.upper()} = {output}")
            out.append(indent + "log_locals(locals(), _namespace)")
            out.append(indent + f"del {kw.upper()}")
            out.append(line)

        elif not s_line.startswith("else:"):
            out.append(line)
            out.append(indent + "log_locals(locals(), _namespace)")
        # elif for_loop_stack and len(indent) < len(for_loop_stack[0]):                   # force a new line after last statement of for loop
        #     prev_indent = for_loop_stack.pop(0)
        #     add_new_line_trigger(out, prev_indent)
        #     out.append(line)
        else:
            out.append(line)


        # if new_line_trigger:
        #     out.append(indent + "NL_TRIGGER = False")
        #     new_line_trigger = False

    out = '\n'.join(out)
    print("Trace table annotations added:")
    print(out)
    return out


###################################################################################################

def get_indent(line: str) -> str:
    '''Find how much indentation a line has
    RETURNS: string - the indentation'''                                        # probably could use regex for this
    space_count = 0
    for char in line:
        if char != " ":
            break
        space_count += 1
    return (space_count * " ")

###################################################################################################

def convert_to_var(expression: str) -> str:
    '''Take a logical expression and convert it
    to a variable name
    RETURNS: string - the expression as a variable name'''
    if not expression[0].isalpha():
        expression = "_" + expression



    out = ""
    token = ""
    expression = expression.replace(" ", "")

    token_found = False
    for e in expression:
        print(e, out, token)

        if e.isalpha() or e.isdigit():
            out += e
            token_found = False
        elif e == "_" and not token_found:
            out += e
        else:
            token += e

        replacement = SYMBOL_REPS.get(token.strip())
        if replacement:
            token = ""
            out += replacement
            token_found = True
        else:
            if len(token.strip()) == 2:
                token = ""

        token = token.replace("_", "")


    return out

###################################################################################################

def stringify_value(value) -> str:
    '''Add quote syntax to strings / chars for the trace table
    to match exam board expectations
    RETURNS: string - string value with quotes added'''
    if type(value) != str or (value[0] == '"' == value[-1]):
        return value

    quoted_value = f'"{value}"'                                                     # double quotes for STRING
    if len(value) == 1:
        quoted_value = f"'{value}'"                                                 # single quotes for CHAR
    return quoted_value

###################################################################################################

def parse_exec_q(code: str) -> str:
    '''Iterate through some program code and allow the program to annotate its own
    statement execution order (i.e 'program counter')
    RETURNS: string - a new version of the code with the annotation enabled'''

    out = []

    line_count = 0
    for line in code.split("\n"):
        s_line = line.strip()

        track_line = f"g.exec_q.append({line_count})"

        indent = get_indent(line)

        if not s_line:                                                              # strip out blank lines
            continue
        if any(s_line.startswith(kw) for kw in CONTROL_STATEMENTS[4:]):             # line number AFTER certain keywords
            out.append(line)
            out.append(indent + SPACE4 + track_line)
        elif "if" in s_line[:4]:                                                    # line number during if / elif eval
            line = line.replace("if ", f"if log_line({line_count}) and ")
            out.append(line)
        elif "while" == s_line[:5]:                                                 # line number during while eval
            line = line.replace("while ", f"while log_line({line_count}) and ")
            out.append(line)
        elif s_line.startswith("else"):                                             # line number during else (→ elif True)
            out.append(line.replace("else:", f"elif log_line({line_count}):"))
        else:                                                                       # otherwise line number before line
            out.append(indent + track_line)
            out.append(line)

        line_count += 1

    return '\n'.join(out)

###################################################################################################

def log_line(i: int) -> bool:
    '''Log the instruction line number currently being executed.
    RETURNS: True so can also be used in a conditional structure'''
    g.exec_q.append(i)
    return True

###################################################################################################

def log_locals(locals, _namespace="__main__()", extra_condition=None):
    '''Log the memory changes at a given point whilst a program is
    being executed.
    RETURNS: True so can also be used in a conditional structure'''


    if extra_condition:                                                # check if logical exp is being evaluated too
        locals.update(extra_condition)

    filtered_locals = dict(locals)                                     # make a copy to allow changes

    for local, value in locals.items():
        if "<function" in str(value):                                  # remove function memory address references
            filtered_locals.pop(local)
        elif len(str(value)) > MAX_CELL_LENGTH:                        # assume if it's really long we don't want it
            filtered_locals.pop(local)
        elif local in REMOVE_VARS:
            filtered_locals.pop(local)
        else:
            filtered_locals[local] = stringify_value(value)

    # will NOT work if there are other brackets in func definition...

    print("Name space is ", _namespace)
    ns_params = _namespace.split("(")[1][:-1]                    # extract the params from the function namespace
    print("Ns params", ns_params)
    ns_func = _namespace.split("(")[0]                           # extract the function name

    resolved_params = []

    for param in ns_params.replace(" ", "").split("^%"):         # lookup the parameter values to resolve references
        if param:
            try:
                resolved_value = str(stringify_value(filtered_locals[param]))
            except KeyError:                                    # non-literals no need to resolve
                resolved_value = stringify_value(param)
            resolved_params.append(resolved_value)

    _namespace = f"{ns_func}({', '.join(resolved_params)})"      # reconstruct the namespace name



    try:
        g.trace_table[_namespace].append(dict(filtered_locals))    # add this memory to that table
    except KeyError:
        g.trace_table[_namespace] = [dict(filtered_locals)]        # create table if needed
    return True

###################################################################################################

def refactor_inputs_as_prints(code: str) -> str:
    '''Replace references to input() with prints
    RETURNS: string - reformatted code with completed input substitutions'''
    out = ""

    for line in code.splitlines():
        if "input(" in line:

            indent = get_indent(line)
            var, input_statement = line.split("=")

            prompt = input_statement.replace("input(", "").strip()[:-1]
            out += indent + f'print({prompt})\n'


        out += line + '\n'

    return out

###################################################################################################

def _get_next_input(prompt):
    '''Get the next user-provided input to mock input() in the program'''
    return g.inputs.pop(0)

###################################################################################################

def get_execution_meta(_code, _inputs=None):

    g.exec_q = []
    g.trace_table = {}


    _code = _code.replace("\t", SPACE4)
    exec(parse_exec_q(_code))

    if _inputs:
        _code = refactor_inputs_as_prints(_code)
        _code = _code.replace("input(", "_get_next_input(")
        g.inputs = _inputs


    exec(get_trace_table(_code).replace('"$%', "").replace('$%"', ""))

    print("PRINTING META")
    for row, data in g.trace_table.items():
        print(row)
        for d in data:
            print(d)

    g.trace_table.pop("<module>()")

    return g.exec_q, g.trace_table

###################################################################################################

def run_tests():

    for i, t in enumerate(tests[-1:]):
        print(f"test {i+1}")

        exec_q, trace_table = get_execution_meta(t)

        print("EXECUTION Q: ", exec_q)

        print("TRACE TABLE DATA: ")
        for namespace, data in trace_table.items():
            print("NAMESPACE", namespace)
            for row in data:
                print("\t", row)



###################################################################################################

tests = ['''def main():
    def recursive_def_dont_work(x):
        if x < 10:
            return recursive_def_dont_work(x+1)
        else:
            return x
    recursive_def_dont_work(1)
main()''',
    
    
'''def main():

    def func(a, b, c):
        print("Whattt")

        if a > b:
            t = "hello"
            if a == c:
                t *= 2
        elif b > c:
            t = "no"
        else:
            t = "yesno"

        return t

    x = func(3, 2, 1)
    print(x)
print("hi")
main()
print("What's going on")
''',

'''
def main():
    x = 5
    while x < 50:
        x += 1
        print(x)
main()
''',

'''
def main():
    def x(a, b):
        return a + b
    
    def y(a, b):
        return a * b
    
    for i in range(3):
        for j in range(3):
            print(x(i, j), y(i, j))
    
main()
''',
'''
def main():
    x = 2
    y = 10
    print("Hello world")
    return x + y
result = main()
print(result)''',

'''def __main__():
    def go():
        x = 10
        for i in range(5):
            print(i)
            print(x)
            x += 1
    go()
__main__()'''


]

if __name__ == "__main__":
    run_tests()