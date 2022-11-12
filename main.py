from flask import Flask, render_template, Markup, request

from os import listdir
from markup_trace_table import create_tables, markup_code
from prep_animations import prep_line_animations, prep_table_animations


app = Flask(__name__)

with app.app_context():
        import annotate_execution

def add_wrapper(code):
	if code.split("\n")[0] != "def __main__():":
		code = "\n".join("\t" + line for line in code.split("\n"))
		code = "def __main__():\n" + code
		code = code + "\n__main__()"
	return code


def strip_blanks(code):
	return "\n".join(line for line in code.splitlines() if len(line.strip()))

@app.route('/submit_code', methods=["POST"])
def submit():

	code = request.form.get("code_submit").strip()
	inputs = request.form.get("inputs").strip().replace(" ", "").split(",")

	wrapped_code = strip_blanks(add_wrapper(code))


	code = strip_blanks(code)

	exec_q, tt_data = annotate_execution.get_execution_meta(wrapped_code, inputs)

	print(exec_q)
	anim = prep_line_animations(exec_q)
	print(anim)

	tables = create_tables(tt_data)

	return render_template("display.html", tables=tables, code=markup_code(code), exec_q=exec_q, line_animation=anim)

#################

@app.route('/')
def index():

	examples = {}
	for fn in listdir("test_cases"):
		if not fn.endswith("py"):	continue
		with open("test_cases/"+fn) as f:
			examples[fn] = f.read()


	return render_template("submit.html", examples=examples, tables=None, code="")

app.run()

