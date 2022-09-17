from flask import Markup

from collections import OrderedDict

from config import SYMBOL_REPS

####################################################################################

def add_new_row(this_row: dict, headings: list) -> str:
	'''Convert Python dict into HTML table row'''

	return '<tr>' + ''.join(f'<td class="i{this_row[h][1]}"><span>{this_row[h][0]}</span></td>' for h in headings.keys()) + '</tr>\n'

####################################################################################

def prepare_table_headings(headings: dict, namespace: str):
	'''Label top row with function namespace name
	Label second row with trace table headings + lookup symbol equivalents'''
	reformatted_headings = []

	for heading in headings.keys():
		for symbol, code in SYMBOL_REPS.items():
			heading = heading.replace(code, symbol)
		reformatted_headings.append(heading)

	ns_stripped = namespace
	for rep in ",()[]":
		ns_stripped = ns_stripped.replace(rep, '_')

	html = ""
	heading_row = "".join(f"<th>{h}</th>" for h in reformatted_headings)
	html += f"<table id={ns_stripped}><tr><th colspan={len(headings)}>{namespace}</th></tr>\n"
	html += f"<tr>{heading_row}</tr>\n"

	return html

####################################################################################

def create_tables(tt_data):
	html = ""

	instruction_count = 0


	for namespace, table in tt_data.items():
		headings = OrderedDict()
		for row in table:
			for k in row.keys():
				headings.update({k:None})

		if "NL_TRIGGER" in headings:
			headings.pop("NL_TRIGGER")

		cols = len(headings)

		print("This table is: ", namespace)

		print("headings are", headings)

		html += prepare_table_headings(headings, namespace)

		current = dict(table[0])
		new_row = False
		this_row = {}

		print("Headings are", headings)

		blank_row = {h:('', -1)  for h in headings.keys()}

		current_values = dict(blank_row)
		this_row = dict(blank_row)



		while len(table):

			this_instruction = table.pop(0)

			print("This instruction is", this_instruction)

			new_line = this_instruction.get("NL_TRIGGER")
			if new_line:

				print("New line because trigger")
				html += add_new_row(this_row, headings)
				this_row = dict(blank_row)

				this_instruction.pop("NL_TRIGGER")

			for column, value in this_instruction.items():


				if current_values[column][0] == '':
					current_values[column] = (value, instruction_count)
					this_row[column] =  (value, instruction_count)
				elif current_values[column][0] != value:
					if this_row[column][0] != '':
						print(f"New line because {value} is different to {current_values[column]} for {column}")
						html += add_new_row(this_row, headings)
						this_row = dict(blank_row)
					current_values[column] =  (value, instruction_count)
					this_row[column] =  (value, instruction_count)

			instruction_count += 1

		html += add_new_row(this_row, headings)

		html += "</table>\n"

	print(html)

	return Markup(html)

####################################################################################

def markup_code(code):
	TABSPACE = "&nbsp;" * 4
	code = code.replace("\t", TABSPACE)
	code = code.replace("    ", TABSPACE)

	code = "".join(f"<p>{line}</p>" for line in code.splitlines())

	return Markup('<div id="code_display">' + code + "</code>")


####################################################################################

def run_tests(tests):

	for i, t in enumerate(tests):
		print(f"TEST {i+1}")
		print()
		create_tables(t)
		input()

tests = [{'__main__()': [{}, {}],
		  'go()': [{}, {'x': 10},
				   {'x': 10, 'NL_TRIGGER': True},
				   {'x': 10, 'NL_TRIGGER': False, 'i': 0},
				   {'x': 10, 'NL_TRIGGER': False, 'i': 0, 'PRINT': 0},
				   {'x': 10, 'NL_TRIGGER': False, 'i': 0, 'PRINT': 10},
				   {'x': 11, 'NL_TRIGGER': False, 'i': 0, 'PRINT': 10},
				   {'x': 11, 'NL_TRIGGER': False, 'i': 1, 'PRINT': 10},
				   {'x': 11, 'NL_TRIGGER': False, 'i': 1, 'PRINT': 1},
				   {'x': 11, 'NL_TRIGGER': False, 'i': 1, 'PRINT': 11}, {'x': 12, 'NL_TRIGGER': False, 'i': 1, 'PRINT': 11}, {'x': 12, 'NL_TRIGGER': False, 'i': 2, 'PRINT': 11}, {'x': 12, 'NL_TRIGGER': False, 'i': 2, 'PRINT': 2}, {'x': 12, 'NL_TRIGGER': False, 'i': 2, 'PRINT': 12}, {'x': 13, 'NL_TRIGGER': False, 'i': 2, 'PRINT': 12}, {'x': 13, 'NL_TRIGGER': False, 'i': 3, 'PRINT': 12}, {'x': 13, 'NL_TRIGGER': False, 'i': 3, 'PRINT': 3}, {'x': 13, 'NL_TRIGGER': False, 'i': 3, 'PRINT': 13}, {'x': 14, 'NL_TRIGGER': False, 'i': 3, 'PRINT': 13}, {'x': 14, 'NL_TRIGGER': False, 'i': 4, 'PRINT': 13}, {'x': 14, 'NL_TRIGGER': False, 'i': 4, 'PRINT': 4}, {'x': 14, 'NL_TRIGGER': False, 'i': 4, 'PRINT': 14}, {'x': 15, 'NL_TRIGGER': False, 'i': 4, 'PRINT': 14}], 'main()': [{}]},
		 {'main()': [{}, {'x': 2}, {'x': 2, 'y': 10}, {'x': 2, 'y': 10, 'PRINT': '"Hello world"'}, {'x': 2, 'y': 10, 'PRINT': '"Hello world"', 'RETURN': 12}, {'result': 12}, {'result': 12, 'PRINT': 12}]},
		 {'main()': [{'PRINT': 'hi'}, {}, {'x': 'hello'}, {'x': 'hello', 'PRINT': 'hello'}, {'PRINT': 'hi'}, {'PRINT': "What's going on"}], 'func(3, 2, 1)': [{'a': 3, 'b': 2, 'c': 1}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt'}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello'}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello', 'a==c': False}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello', 'a==c': False, 'RETURN': 'hello'}]},
		 {'main()': [{'PRINT': 'hi'}, {}, {'x': 'hello'}, {'x': 'hello', 'PRINT': 'hello'}, {'PRINT': 'hi'}, {'PRINT': "What's going on"}, {}, {'x': 5}, {'x': 5, 'x<50': True}, {'x': 6, 'x<50': True}, {'x': 6, 'x<50': True, 'PRINT': 6}, {'x': 6, 'x<50': True, 'PRINT': 6}, {'x': 7, 'x<50': True, 'PRINT': 6}, {'x': 7, 'x<50': True, 'PRINT': 7}, {'x': 7, 'x<50': True, 'PRINT': 7}, {'x': 8, 'x<50': True, 'PRINT': 7}, {'x': 8, 'x<50': True, 'PRINT': 8}, {'x': 8, 'x<50': True, 'PRINT': 8}, {'x': 9, 'x<50': True, 'PRINT': 8}, {'x': 9, 'x<50': True, 'PRINT': 9}, {'x': 9, 'x<50': True, 'PRINT': 9}, {'x': 10, 'x<50': True, 'PRINT': 9}, {'x': 10, 'x<50': True, 'PRINT': 10}, {'x': 10, 'x<50': True, 'PRINT': 10}, {'x': 11, 'x<50': True, 'PRINT': 10}, {'x': 11, 'x<50': True, 'PRINT': 11}, {'x': 11, 'x<50': True, 'PRINT': 11}, {'x': 12, 'x<50': True, 'PRINT': 11}, {'x': 12, 'x<50': True, 'PRINT': 12}, {'x': 12, 'x<50': True, 'PRINT': 12}, {'x': 13, 'x<50': True, 'PRINT': 12}, {'x': 13, 'x<50': True, 'PRINT': 13}, {'x': 13, 'x<50': True, 'PRINT': 13}, {'x': 14, 'x<50': True, 'PRINT': 13}, {'x': 14, 'x<50': True, 'PRINT': 14}, {'x': 14, 'x<50': True, 'PRINT': 14}, {'x': 15, 'x<50': True, 'PRINT': 14}, {'x': 15, 'x<50': True, 'PRINT': 15}, {'x': 15, 'x<50': True, 'PRINT': 15}, {'x': 16, 'x<50': True, 'PRINT': 15}, {'x': 16, 'x<50': True, 'PRINT': 16}, {'x': 16, 'x<50': True, 'PRINT': 16}, {'x': 17, 'x<50': True, 'PRINT': 16}, {'x': 17, 'x<50': True, 'PRINT': 17}, {'x': 17, 'x<50': True, 'PRINT': 17}, {'x': 18, 'x<50': True, 'PRINT': 17}, {'x': 18, 'x<50': True, 'PRINT': 18}, {'x': 18, 'x<50': True, 'PRINT': 18}, {'x': 19, 'x<50': True, 'PRINT': 18}, {'x': 19, 'x<50': True, 'PRINT': 19}, {'x': 19, 'x<50': True, 'PRINT': 19}, {'x': 20, 'x<50': True, 'PRINT': 19}, {'x': 20, 'x<50': True, 'PRINT': 20}, {'x': 20, 'x<50': True, 'PRINT': 20}, {'x': 21, 'x<50': True, 'PRINT': 20}, {'x': 21, 'x<50': True, 'PRINT': 21}, {'x': 21, 'x<50': True, 'PRINT': 21}, {'x': 22, 'x<50': True, 'PRINT': 21}, {'x': 22, 'x<50': True, 'PRINT': 22}, {'x': 22, 'x<50': True, 'PRINT': 22}, {'x': 23, 'x<50': True, 'PRINT': 22}, {'x': 23, 'x<50': True, 'PRINT': 23}, {'x': 23, 'x<50': True, 'PRINT': 23}, {'x': 24, 'x<50': True, 'PRINT': 23}, {'x': 24, 'x<50': True, 'PRINT': 24}, {'x': 24, 'x<50': True, 'PRINT': 24}, {'x': 25, 'x<50': True, 'PRINT': 24}, {'x': 25, 'x<50': True, 'PRINT': 25}, {'x': 25, 'x<50': True, 'PRINT': 25}, {'x': 26, 'x<50': True, 'PRINT': 25}, {'x': 26, 'x<50': True, 'PRINT': 26}, {'x': 26, 'x<50': True, 'PRINT': 26}, {'x': 27, 'x<50': True, 'PRINT': 26}, {'x': 27, 'x<50': True, 'PRINT': 27}, {'x': 27, 'x<50': True, 'PRINT': 27}, {'x': 28, 'x<50': True, 'PRINT': 27}, {'x': 28, 'x<50': True, 'PRINT': 28}, {'x': 28, 'x<50': True, 'PRINT': 28}, {'x': 29, 'x<50': True, 'PRINT': 28}, {'x': 29, 'x<50': True, 'PRINT': 29}, {'x': 29, 'x<50': True, 'PRINT': 29}, {'x': 30, 'x<50': True, 'PRINT': 29}, {'x': 30, 'x<50': True, 'PRINT': 30}, {'x': 30, 'x<50': True, 'PRINT': 30}, {'x': 31, 'x<50': True, 'PRINT': 30}, {'x': 31, 'x<50': True, 'PRINT': 31}, {'x': 31, 'x<50': True, 'PRINT': 31}, {'x': 32, 'x<50': True, 'PRINT': 31}, {'x': 32, 'x<50': True, 'PRINT': 32}, {'x': 32, 'x<50': True, 'PRINT': 32}, {'x': 33, 'x<50': True, 'PRINT': 32}, {'x': 33, 'x<50': True, 'PRINT': 33}, {'x': 33, 'x<50': True, 'PRINT': 33}, {'x': 34, 'x<50': True, 'PRINT': 33}, {'x': 34, 'x<50': True, 'PRINT': 34}, {'x': 34, 'x<50': True, 'PRINT': 34}, {'x': 35, 'x<50': True, 'PRINT': 34}, {'x': 35, 'x<50': True, 'PRINT': 35}, {'x': 35, 'x<50': True, 'PRINT': 35}, {'x': 36, 'x<50': True, 'PRINT': 35}, {'x': 36, 'x<50': True, 'PRINT': 36}, {'x': 36, 'x<50': True, 'PRINT': 36}, {'x': 37, 'x<50': True, 'PRINT': 36}, {'x': 37, 'x<50': True, 'PRINT': 37}, {'x': 37, 'x<50': True, 'PRINT': 37}, {'x': 38, 'x<50': True, 'PRINT': 37}, {'x': 38, 'x<50': True, 'PRINT': 38}, {'x': 38, 'x<50': True, 'PRINT': 38}, {'x': 39, 'x<50': True, 'PRINT': 38}, {'x': 39, 'x<50': True, 'PRINT': 39}, {'x': 39, 'x<50': True, 'PRINT': 39}, {'x': 40, 'x<50': True, 'PRINT': 39}, {'x': 40, 'x<50': True, 'PRINT': 40}, {'x': 40, 'x<50': True, 'PRINT': 40}, {'x': 41, 'x<50': True, 'PRINT': 40}, {'x': 41, 'x<50': True, 'PRINT': 41}, {'x': 41, 'x<50': True, 'PRINT': 41}, {'x': 42, 'x<50': True, 'PRINT': 41}, {'x': 42, 'x<50': True, 'PRINT': 42}, {'x': 42, 'x<50': True, 'PRINT': 42}, {'x': 43, 'x<50': True, 'PRINT': 42}, {'x': 43, 'x<50': True, 'PRINT': 43}, {'x': 43, 'x<50': True, 'PRINT': 43}, {'x': 44, 'x<50': True, 'PRINT': 43}, {'x': 44, 'x<50': True, 'PRINT': 44}, {'x': 44, 'x<50': True, 'PRINT': 44}, {'x': 45, 'x<50': True, 'PRINT': 44}, {'x': 45, 'x<50': True, 'PRINT': 45}, {'x': 45, 'x<50': True, 'PRINT': 45}, {'x': 46, 'x<50': True, 'PRINT': 45}, {'x': 46, 'x<50': True, 'PRINT': 46}, {'x': 46, 'x<50': True, 'PRINT': 46}, {'x': 47, 'x<50': True, 'PRINT': 46}, {'x': 47, 'x<50': True, 'PRINT': 47}, {'x': 47, 'x<50': True, 'PRINT': 47}, {'x': 48, 'x<50': True, 'PRINT': 47}, {'x': 48, 'x<50': True, 'PRINT': 48}, {'x': 48, 'x<50': True, 'PRINT': 48}, {'x': 49, 'x<50': True, 'PRINT': 48}, {'x': 49, 'x<50': True, 'PRINT': 49}, {'x': 49, 'x<50': True, 'PRINT': 49}, {'x': 50, 'x<50': True, 'PRINT': 49}, {'x': 50, 'x<50': True, 'PRINT': 50}, {'x': 50, 'x<50': False, 'PRINT': 50}, {}], 'func(3, 2, 1)': [{'a': 3, 'b': 2, 'c': 1}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt'}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello'}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello', 'a==c': False}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello', 'a==c': False, 'RETURN': 'hello'}]},
		 {'main()': [{'PRINT': 'hi'}, {}, {'x': 'hello'}, {'x': 'hello', 'PRINT': 'hello'}, {'PRINT': 'hi'}, {'PRINT': "What's going on"}, {}, {'x': 5}, {'x': 5, 'x<50': True}, {'x': 6, 'x<50': True}, {'x': 6, 'x<50': True, 'PRINT': 6}, {'x': 6, 'x<50': True, 'PRINT': 6}, {'x': 7, 'x<50': True, 'PRINT': 6}, {'x': 7, 'x<50': True, 'PRINT': 7}, {'x': 7, 'x<50': True, 'PRINT': 7}, {'x': 8, 'x<50': True, 'PRINT': 7}, {'x': 8, 'x<50': True, 'PRINT': 8}, {'x': 8, 'x<50': True, 'PRINT': 8}, {'x': 9, 'x<50': True, 'PRINT': 8}, {'x': 9, 'x<50': True, 'PRINT': 9}, {'x': 9, 'x<50': True, 'PRINT': 9}, {'x': 10, 'x<50': True, 'PRINT': 9}, {'x': 10, 'x<50': True, 'PRINT': 10}, {'x': 10, 'x<50': True, 'PRINT': 10}, {'x': 11, 'x<50': True, 'PRINT': 10}, {'x': 11, 'x<50': True, 'PRINT': 11}, {'x': 11, 'x<50': True, 'PRINT': 11}, {'x': 12, 'x<50': True, 'PRINT': 11}, {'x': 12, 'x<50': True, 'PRINT': 12}, {'x': 12, 'x<50': True, 'PRINT': 12}, {'x': 13, 'x<50': True, 'PRINT': 12}, {'x': 13, 'x<50': True, 'PRINT': 13}, {'x': 13, 'x<50': True, 'PRINT': 13}, {'x': 14, 'x<50': True, 'PRINT': 13}, {'x': 14, 'x<50': True, 'PRINT': 14}, {'x': 14, 'x<50': True, 'PRINT': 14}, {'x': 15, 'x<50': True, 'PRINT': 14}, {'x': 15, 'x<50': True, 'PRINT': 15}, {'x': 15, 'x<50': True, 'PRINT': 15}, {'x': 16, 'x<50': True, 'PRINT': 15}, {'x': 16, 'x<50': True, 'PRINT': 16}, {'x': 16, 'x<50': True, 'PRINT': 16}, {'x': 17, 'x<50': True, 'PRINT': 16}, {'x': 17, 'x<50': True, 'PRINT': 17}, {'x': 17, 'x<50': True, 'PRINT': 17}, {'x': 18, 'x<50': True, 'PRINT': 17}, {'x': 18, 'x<50': True, 'PRINT': 18}, {'x': 18, 'x<50': True, 'PRINT': 18}, {'x': 19, 'x<50': True, 'PRINT': 18}, {'x': 19, 'x<50': True, 'PRINT': 19}, {'x': 19, 'x<50': True, 'PRINT': 19}, {'x': 20, 'x<50': True, 'PRINT': 19}, {'x': 20, 'x<50': True, 'PRINT': 20}, {'x': 20, 'x<50': True, 'PRINT': 20}, {'x': 21, 'x<50': True, 'PRINT': 20}, {'x': 21, 'x<50': True, 'PRINT': 21}, {'x': 21, 'x<50': True, 'PRINT': 21}, {'x': 22, 'x<50': True, 'PRINT': 21}, {'x': 22, 'x<50': True, 'PRINT': 22}, {'x': 22, 'x<50': True, 'PRINT': 22}, {'x': 23, 'x<50': True, 'PRINT': 22}, {'x': 23, 'x<50': True, 'PRINT': 23}, {'x': 23, 'x<50': True, 'PRINT': 23}, {'x': 24, 'x<50': True, 'PRINT': 23}, {'x': 24, 'x<50': True, 'PRINT': 24}, {'x': 24, 'x<50': True, 'PRINT': 24}, {'x': 25, 'x<50': True, 'PRINT': 24}, {'x': 25, 'x<50': True, 'PRINT': 25}, {'x': 25, 'x<50': True, 'PRINT': 25}, {'x': 26, 'x<50': True, 'PRINT': 25}, {'x': 26, 'x<50': True, 'PRINT': 26}, {'x': 26, 'x<50': True, 'PRINT': 26}, {'x': 27, 'x<50': True, 'PRINT': 26}, {'x': 27, 'x<50': True, 'PRINT': 27}, {'x': 27, 'x<50': True, 'PRINT': 27}, {'x': 28, 'x<50': True, 'PRINT': 27}, {'x': 28, 'x<50': True, 'PRINT': 28}, {'x': 28, 'x<50': True, 'PRINT': 28}, {'x': 29, 'x<50': True, 'PRINT': 28}, {'x': 29, 'x<50': True, 'PRINT': 29}, {'x': 29, 'x<50': True, 'PRINT': 29}, {'x': 30, 'x<50': True, 'PRINT': 29}, {'x': 30, 'x<50': True, 'PRINT': 30}, {'x': 30, 'x<50': True, 'PRINT': 30}, {'x': 31, 'x<50': True, 'PRINT': 30}, {'x': 31, 'x<50': True, 'PRINT': 31}, {'x': 31, 'x<50': True, 'PRINT': 31}, {'x': 32, 'x<50': True, 'PRINT': 31}, {'x': 32, 'x<50': True, 'PRINT': 32}, {'x': 32, 'x<50': True, 'PRINT': 32}, {'x': 33, 'x<50': True, 'PRINT': 32}, {'x': 33, 'x<50': True, 'PRINT': 33}, {'x': 33, 'x<50': True, 'PRINT': 33}, {'x': 34, 'x<50': True, 'PRINT': 33}, {'x': 34, 'x<50': True, 'PRINT': 34}, {'x': 34, 'x<50': True, 'PRINT': 34}, {'x': 35, 'x<50': True, 'PRINT': 34}, {'x': 35, 'x<50': True, 'PRINT': 35}, {'x': 35, 'x<50': True, 'PRINT': 35}, {'x': 36, 'x<50': True, 'PRINT': 35}, {'x': 36, 'x<50': True, 'PRINT': 36}, {'x': 36, 'x<50': True, 'PRINT': 36}, {'x': 37, 'x<50': True, 'PRINT': 36}, {'x': 37, 'x<50': True, 'PRINT': 37}, {'x': 37, 'x<50': True, 'PRINT': 37}, {'x': 38, 'x<50': True, 'PRINT': 37}, {'x': 38, 'x<50': True, 'PRINT': 38}, {'x': 38, 'x<50': True, 'PRINT': 38}, {'x': 39, 'x<50': True, 'PRINT': 38}, {'x': 39, 'x<50': True, 'PRINT': 39}, {'x': 39, 'x<50': True, 'PRINT': 39}, {'x': 40, 'x<50': True, 'PRINT': 39}, {'x': 40, 'x<50': True, 'PRINT': 40}, {'x': 40, 'x<50': True, 'PRINT': 40}, {'x': 41, 'x<50': True, 'PRINT': 40}, {'x': 41, 'x<50': True, 'PRINT': 41}, {'x': 41, 'x<50': True, 'PRINT': 41}, {'x': 42, 'x<50': True, 'PRINT': 41}, {'x': 42, 'x<50': True, 'PRINT': 42}, {'x': 42, 'x<50': True, 'PRINT': 42}, {'x': 43, 'x<50': True, 'PRINT': 42}, {'x': 43, 'x<50': True, 'PRINT': 43}, {'x': 43, 'x<50': True, 'PRINT': 43}, {'x': 44, 'x<50': True, 'PRINT': 43}, {'x': 44, 'x<50': True, 'PRINT': 44}, {'x': 44, 'x<50': True, 'PRINT': 44}, {'x': 45, 'x<50': True, 'PRINT': 44}, {'x': 45, 'x<50': True, 'PRINT': 45}, {'x': 45, 'x<50': True, 'PRINT': 45}, {'x': 46, 'x<50': True, 'PRINT': 45}, {'x': 46, 'x<50': True, 'PRINT': 46}, {'x': 46, 'x<50': True, 'PRINT': 46}, {'x': 47, 'x<50': True, 'PRINT': 46}, {'x': 47, 'x<50': True, 'PRINT': 47}, {'x': 47, 'x<50': True, 'PRINT': 47}, {'x': 48, 'x<50': True, 'PRINT': 47}, {'x': 48, 'x<50': True, 'PRINT': 48}, {'x': 48, 'x<50': True, 'PRINT': 48}, {'x': 49, 'x<50': True, 'PRINT': 48}, {'x': 49, 'x<50': True, 'PRINT': 49}, {'x': 49, 'x<50': True, 'PRINT': 49}, {'x': 50, 'x<50': True, 'PRINT': 49}, {'x': 50, 'x<50': True, 'PRINT': 50}, {'x': 50, 'x<50': False, 'PRINT': 50}, {}, {}, {'i': 0}, {'i': 0, 'j': 0}, {'i': 0, 'j': 0, 'PRINT': (0, 0)}, {'i': 0, 'j': 1, 'PRINT': (0, 0)}, {'i': 0, 'j': 1, 'PRINT': (1, 0)}, {'i': 0, 'j': 2, 'PRINT': (1, 0)}, {'i': 0, 'j': 2, 'PRINT': (2, 0)}, {'i': 1, 'j': 2, 'PRINT': (2, 0)}, {'i': 1, 'j': 0, 'PRINT': (2, 0)}, {'i': 1, 'j': 0, 'PRINT': (1, 0)}, {'i': 1, 'j': 1, 'PRINT': (1, 0)}, {'i': 1, 'j': 1, 'PRINT': (2, 1)}, {'i': 1, 'j': 2, 'PRINT': (2, 1)}, {'i': 1, 'j': 2, 'PRINT': (3, 2)}, {'i': 2, 'j': 2, 'PRINT': (3, 2)}, {'i': 2, 'j': 0, 'PRINT': (3, 2)}, {'i': 2, 'j': 0, 'PRINT': (2, 0)}, {'i': 2, 'j': 1, 'PRINT': (2, 0)}, {'i': 2, 'j': 1, 'PRINT': (3, 2)}, {'i': 2, 'j': 2, 'PRINT': (3, 2)}, {'i': 2, 'j': 2, 'PRINT': (4, 4)}, {}], 'func(3, 2, 1)': [{'a': 3, 'b': 2, 'c': 1}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt'}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello'}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello', 'a==c': False}, {'a': 3, 'b': 2, 'c': 1, 'PRINT': 'Whattt', 'a>b': True, 't': 'hello', 'a==c': False, 'RETURN': 'hello'}], 'x(0, 0)': [{'a': 0, 'b': 0}, {'a': 0, 'b': 0, 'RETURN': 0}, {'a': 0, 'b': 0}, {'a': 0, 'b': 0, 'RETURN': 0}], 'y(0, 0)': [{'a': 0, 'b': 0}, {'a': 0, 'b': 0, 'RETURN': 0}, {'a': 0, 'b': 0}, {'a': 0, 'b': 0, 'RETURN': 0}], 'x(0, 1)': [{'a': 0, 'b': 1}, {'a': 0, 'b': 1, 'RETURN': 1}, {'a': 0, 'b': 1}, {'a': 0, 'b': 1, 'RETURN': 1}], 'y(0, 1)': [{'a': 0, 'b': 1}, {'a': 0, 'b': 1, 'RETURN': 0}, {'a': 0, 'b': 1}, {'a': 0, 'b': 1, 'RETURN': 0}], 'x(0, 2)': [{'a': 0, 'b': 2}, {'a': 0, 'b': 2, 'RETURN': 2}, {'a': 0, 'b': 2}, {'a': 0, 'b': 2, 'RETURN': 2}], 'y(0, 2)': [{'a': 0, 'b': 2}, {'a': 0, 'b': 2, 'RETURN': 0}, {'a': 0, 'b': 2}, {'a': 0, 'b': 2, 'RETURN': 0}], 'x(1, 0)': [{'a': 1, 'b': 0}, {'a': 1, 'b': 0, 'RETURN': 1}, {'a': 1, 'b': 0}, {'a': 1, 'b': 0, 'RETURN': 1}], 'y(1, 0)': [{'a': 1, 'b': 0}, {'a': 1, 'b': 0, 'RETURN': 0}, {'a': 1, 'b': 0}, {'a': 1, 'b': 0, 'RETURN': 0}], 'x(1, 1)': [{'a': 1, 'b': 1}, {'a': 1, 'b': 1, 'RETURN': 2}, {'a': 1, 'b': 1}, {'a': 1, 'b': 1, 'RETURN': 2}], 'y(1, 1)': [{'a': 1, 'b': 1}, {'a': 1, 'b': 1, 'RETURN': 1}, {'a': 1, 'b': 1}, {'a': 1, 'b': 1, 'RETURN': 1}], 'x(1, 2)': [{'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'RETURN': 3}, {'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'RETURN': 3}], 'y(1, 2)': [{'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'RETURN': 2}, {'a': 1, 'b': 2}, {'a': 1, 'b': 2, 'RETURN': 2}], 'x(2, 0)': [{'a': 2, 'b': 0}, {'a': 2, 'b': 0, 'RETURN': 2}, {'a': 2, 'b': 0}, {'a': 2, 'b': 0, 'RETURN': 2}], 'y(2, 0)': [{'a': 2, 'b': 0}, {'a': 2, 'b': 0, 'RETURN': 0}, {'a': 2, 'b': 0}, {'a': 2, 'b': 0, 'RETURN': 0}], 'x(2, 1)': [{'a': 2, 'b': 1}, {'a': 2, 'b': 1, 'RETURN': 3}, {'a': 2, 'b': 1}, {'a': 2, 'b': 1, 'RETURN': 3}], 'y(2, 1)': [{'a': 2, 'b': 1}, {'a': 2, 'b': 1, 'RETURN': 2}, {'a': 2, 'b': 1}, {'a': 2, 'b': 1, 'RETURN': 2}], 'x(2, 2)': [{'a': 2, 'b': 2}, {'a': 2, 'b': 2, 'RETURN': 4}, {'a': 2, 'b': 2}, {'a': 2, 'b': 2, 'RETURN': 4}], 'y(2, 2)': [{'a': 2, 'b': 2}, {'a': 2, 'b': 2, 'RETURN': 4}, {'a': 2, 'b': 2}, {'a': 2, 'b': 2, 'RETURN': 4}]}]



if __name__ == "__main__":

	run_tests(tests)