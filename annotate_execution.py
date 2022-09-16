SPACE4 = " "*4
SPACE_SIZE = 4

CONTROL_STATEMENTS = 'if,elif,else,def,for,while,try,except'.split(",")

###################################################################################################

def get_trace_table(code):

	out = []
	for line in code.split("\n"):
		s_line = line.strip()
		if not s_line:	continue

		indent = get_indent(line)

		if (def_found := s_line.startswith("def")) or (for_found := s_line.startswith("for")):
			out.append(line)
			indent += SPACE4

			if def_found:
				out.append(indent + "global current_namespace")
				func_call = line.replace("def ", "")[:-1].strip()

				out.append(indent + f"current_namespace = '''{func_call}'''")     # record the current namespace ID

			out.append(indent + "log_locals(locals())")

		elif (if_found := "if" in s_line[:4]) or (while_found := s_line.startswith("while")):
			kw = "if " if if_found else "while "
			condition = line.split(kw)[1][:-1]
			condition = {condition.replace(" ", ""):f"$%eval('{condition}')$%"}
			line = line.replace(f"{kw}", f"{kw}log_locals(locals(), {condition}) and ")
			out.append(line)

		elif (return_found := s_line.startswith("return")) or (print_found := s_line.startswith("print")):
			kw = "return " if return_found else "print("
			_, output = s_line.split(kw)
			if kw == "print(":
				output = output[:-1] # get rid of last bracket
				kw = kw[:-1]

			out.append(indent + f"{kw.upper()} = {output}")
			out.append(indent + "log_locals(locals())")
			out.append(line)
			
		elif not s_line.startswith("else"):
			out.append(line)
			out.append(indent + "log_locals(locals())")
		else:
			out.append(line)







	out = '\n'.join(out)
	print(out)
	return out


###################################################################################################

def get_indent(line):
	space_count = 0
	for char in line:
		if char != " ":
			break
		space_count += 1
	return (space_count * " ")

###################################################################################################

def parse_exec_q(code):

	out = []


	line_count = 0
	for line in code.split("\n"):
		s_line = line.strip()

		track_line = f"exec_q.append({line_count})"

		indent = get_indent(line)

		if not s_line:
			continue

		if s_line.startswith("def"):
			out.append(line)
			out.append(indent + SPACE4 + track_line)
		elif "if" in s_line[:4]:
			line = line.replace("if ", f"if log_line({line_count}) and ")
			out.append(line)
		elif "while" == s_line[:5]:
			line = line.replace("while ", f"while log_line({line_count}) and ")
			out.append(line)
		elif s_line.startswith("else"):
			out.append(line.replace("else:", f"elif log_line({line_count}):"))
		else:
			out.append(indent + track_line)
			out.append(line)

		line_count += 1

	return '\n'.join(out)

###################################################################################################

def log_line(i):
	exec_q.append(i)
	return True

###################################################################################################

def log_locals(locals, extra_condition=None):
	global current_namespace
	if extra_condition:
		locals.update(extra_condition)

	print(locals)

	filtered_locals = dict(locals)

	for local, value in locals.items():
		if "<function" in str(value):
			filtered_locals.pop(local)


	ns_params = current_namespace.split("(")[1][:-1]  # will NOT work if there are other brackets in func definition...
	ns_func = current_namespace.split("(")[0]

	resolved_params = []

	for param in ns_params.replace(" ", "").split(","):
		if param:
			try:
				resolved_value = str(filtered_locals[param])
			except KeyError:
				resolved_value = param
			resolved_params.append(resolved_value)

	current_namespace = ns_func + "(" + ", ".join(resolved_params) + ")"

	try:
		trace_table[current_namespace].append(str(filtered_locals))
	except KeyError:
		trace_table[current_namespace] = [str(filtered_locals)]
	return True

###################################################################################################

def get_execution_meta(code):
	code = code.replace("\t", SPACE4)
	exec(parse_exec_q(code))
	exec(get_trace_table(code).replace('"$%', "").replace('$%"', ""))

	return exec_q, trace_table




###################################################################################################

def run_tests():

	for i, t in enumerate(tests):
		print(f"test {i+1}")

		exec_q, trace_table = get_execution_meta(t)

		print("EXECUTION Q: ", exec_q)

		print("TRACE TABLE DATA: ")
		for namespace, data in trace_table.items():
			print("NAMESPACE", namespace)
			for row in data:
				print("\t", row)

		print()

###################################################################################################

tests = ['''

def main():

	def func(a, b, c):

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

main()
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

exec_q = []
trace_table = {}
run_tests()