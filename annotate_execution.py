SPACE4 = " "*4
SPACE_SIZE = 4

CONTROL_STATEMENTS = 'if,elif,else,def,for,while,try,except'.split(",")

def get_trace_table(code):

	out = []
	for line in code.split("\n"):
		s_line = line.strip()
		if not s_line:	continue

		indent = get_indent(line)

		if any([s_line.startswith(kw) for kw in ["def", "for"]]):
			out.append(line)
			indent += SPACE4
			out.append(indent + "log_locals(locals())")

		elif (if_found := "if" in s_line[:4]) or (while_found := s_line.startswith("while")):
			kw = "if " if if_found else "while "
			condition = line.split(kw)[1][:-1]
			condition = {condition.replace(" ", ""):f"$%eval('{condition}')$%"}
			line = line.replace(f"{kw}", f"{kw}log_locals(locals(), {condition}) and ")
			out.append(line)
		elif (return_found := s_line.startswith("return")) or (print_found := s_line.startswith("print")):
			kw = "print(" if print_found else "return "
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


#########

def get_indent(line):
	space_count = 0
	for char in line:
		if char != " ":
			break
		space_count += 1
	return (space_count * " ")

#########

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


tests = ['''

def test():

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
	
test()
''',


'''
def test():
	x = 5
	while x < 50:
		x += 1
	print(x)
test()
'''


]

from json import dumps

def log_line(i):
	exec_q.append(i)
	return True

def log_locals(locals, extra_condition=None):
	if extra_condition:
		locals.update(extra_condition)

	print(locals)
	input()
	trace_table.append(str(locals))
	return True

def main():

	for i, t in enumerate(tests):
		print(f"test {i+1}")

		code = t.replace("\t", SPACE4)
		exec(parse_exec_q(code))
		print("Statement execution queue: exec_q")

		exec(get_trace_table(code).replace('"$%', "").replace('$%"', ""))
		print("Changes to memory:")
		for row in trace_table:
			print(row)

		print()


exec_q = []
trace_table = []
main()