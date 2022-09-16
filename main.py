from flask import Flask, render_template, Markup, request

import annotate_execution
from markup_trace_table import create_tables, markup_code



app = Flask(__name__)


@app.route('/submit_code', methods=["POST"])
def submit():
	import annotate_execution
	code = request.form.get("code_submit").strip()

	if code.split("\n")[0] != "def __main__():":
		code = "\n".join("\t" + line for line in code.split("\n"))
		code = "def __main__():\n" + code
		code = code + "\n__main__()"

	print(code)

	exec_q, tt_data = annotate_execution.get_execution_meta(code)
	tables = create_tables(tt_data)

	return render_template("index.html", tables=tables, code=code)

#################

@app.route('/')
def index():
	code = '''
def main():
	x = 2
	y = 10
	print("Hello world")
	return x + y
result = main()
print(result)'''

	exec_q, tt_data = annotate_execution.get_execution_meta(code)
	tables = create_tables(tt_data)

	return render_template("index.html", tables=tables, code=code)

app.run()

