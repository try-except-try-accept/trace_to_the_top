from flask import Flask, render_template, Markup, request


from markup_trace_table import create_tables, markup_code



app = Flask(__name__)

with app.app_context():
        import annotate_execution

def add_wrapper(code):
	if code.split("\n")[0] != "def __main__():":
		code = "\n".join("\t" + line for line in code.split("\n"))
		code = "def __main__():\n" + code
		code = code + "\n__main__()"
	return code


@app.route('/submit_code', methods=["POST"])
def submit():

	code = request.form.get("code_submit").strip()
	inputs = request.form.get("inputs").strip().replace(" ", "").split(",")
	orig_code = code

	wrapped_code = add_wrapper(code)

	exec_q, tt_data = annotate_execution.get_execution_meta(wrapped_code, inputs)
	tables = create_tables(tt_data)

	return render_template("index.html", tables=tables, code=orig_code)

#################

@app.route('/')
def index():
	code = '''
def x():
	x = 2
	y = 10
	print("Hello world")
	return x + y
result = x()
print(result)'''

	wrapped_code = add_wrapper(code)

	exec_q, tt_data = annotate_execution.get_execution_meta(wrapped_code)
	tables = create_tables(tt_data)

	return render_template("index.html", tables=tables, code=code)

app.run()

