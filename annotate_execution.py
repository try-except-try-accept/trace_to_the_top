SPACE4 = " "*4
SPACE_SIZE = 4
MAX_CELL_LENGTH = 20
CONTROL_STATEMENTS = 'if,elif,else,while,def,for,try,except'.split(",")
REMOVE_VARS = ["this_func", "params", "namespace"]  # helpers for identifying scope
import inspect

namespace = "main()"
exec_q = []
trace_table = {}

###################################################################################################

def get_trace_table(code: str) -> str:
    '''Iterate through some program code and allow the program to annotate its memory changes
    to create a trace table. Include logical expressions and output statements as well as variable values.
    RETURNS: string - a new version of the code with the annotation enabled'''

    out = []
    for line in code.split("\n"):
        s_line = line.strip()
        if not s_line:    continue                                               # skip blank lines

        indent = get_indent(line)

        this_func = inspect.stack()[0][3]




        if (def_found := s_line.startswith("def")) or \
           (for_found := s_line.startswith("for")):                              # def or for found?

            out.append(line)
            indent += SPACE4



            if def_found:

                params = s_line.split("(")[1][:-2]



                if not params:
                    params = '()'
                else:
                    for delim in ":=":                                               # handle type hints and kwargs
                        params = ",".join(p.split(delim)[0]
                                      for p in params.replace(" ", "").split(","))

                out.append(indent + "this_func = inspect.stack()[0][3]")
                out.append(indent + f"params = {params}")
                out.append(indent + 'namespace = f"{this_func}({params})"')
                out.append(indent + "print(namespace, 'is my namespace')")

            out.append(indent + "log_locals(locals(), namespace)")

        elif (if_found := "if" in s_line[:4]) or \
             (while_found := s_line.startswith("while")):                            # ensure logic exps are recorded
            kw = "if " if if_found else "while "
            cond = s_line.split(kw)[1][:-1]                                          # despace condition to allow var name and
            cond = {convert_to_var(cond):f"$%eval('{cond}')$%"}                      # set up the logic exp to evaluate later
            line = line.replace(kw,
                                f"{kw}log_locals(locals(), namespace, {cond}) and ") # include memory lookup in condition
            out.append(line)

        elif (return_found := s_line.startswith("return")) or \
             (print_found := s_line.startswith("print")):
            kw = "return " if return_found else "print("                             # track print() and return too
            _, output = s_line.split(kw)
            if kw == "print(":
                output = output[:-1]                                                 # get rid of last bracket
                kw = kw[:-1]

            out.append(indent + f"{kw.upper()} = {output}")
            out.append(indent + "log_locals(locals(), namespace)")
            out.append(line)
            
        elif not s_line.startswith("else"):
            out.append(line)
            out.append(indent + "log_locals(locals(), namespace)")
        else:                                                                        # nothing to be added to the trace table for else
            out.append(line)

    out = '\n'.join(out)
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

    return "".join(e if e.isalpha() or e.isdigit() or e == '_' else '_' for e in expression)

###################################################################################################

def stringify_value(value) -> str:
    '''Add quote syntax to strings / chars for the trace table
    to match exam board expectations
    RETURNS: string - string value with quotes added'''
    if type(value) != str:
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

        track_line = f"exec_q.append({line_count})"

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
    exec_q.append(i)
    return True

###################################################################################################

def log_locals(locals, namespace="main()", extra_condition=None):
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


    ns_params = namespace.split("(")[1][:-1]                    # extract the params from the function namespace
    ns_func = namespace.split("(")[0]                           # extract the function name

    resolved_params = []

    for param in ns_params.replace(" ", "").split(","):         # lookup the parameter values to resolve references
        if param:
            try:
                resolved_value = str(stringify_value(filtered_locals[param]))
            except KeyError:                                    # non-literals no need to resolve
                resolved_value = stringify_value(param)
            resolved_params.append(resolved_value)

    namespace = f"{ns_func}({', '.join(resolved_params)})"      # reconstruct the namespace name

    try:
        trace_table[namespace].append(dict(filtered_locals))    # add this memory to that table
    except KeyError:
        trace_table[namespace] = [dict(filtered_locals)]        # create table if needed
    return True

###################################################################################################

def get_execution_meta(code):
    code = code.replace("\t", SPACE4)
    #exec(parse_exec_q(code))



    exec(get_trace_table(code).replace('"$%', "").replace('$%"', ""))

    print(trace_table)

    return exec_q, trace_table

###################################################################################################

def run_tests():

    for i, t in enumerate(tests[1:]):
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
'''

         ]
if __name__ == "__main__":
    run_tests()