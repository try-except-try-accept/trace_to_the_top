from flask import Markup



def prep_line_animations(exec_q):
	css = "<style>"
	selector = '#code_display p:nth-child(instruction) { animation: '
	anim_rule = 'highlight_line 1s linear counts'

	anim_map = {}
	for count, line in enumerate(exec_q):
		this_selector = selector.replace("instruction", str(line))
		this_rule = anim_rule.replace("count", str(count))
		try:
			anim_map[this_selector].append(this_rule)
		except KeyError:
			anim_map[this_selector] = [this_rule]



	return Markup("<style>" + "".join(sel + ",".join(rule) + ";}\n" for sel, rule in anim_map.items()) + "</style>")


def prep_table_animations(exec_q):
	rule = ".iclass_count {animation: highlight_cell 1s linear secs forwards;}"
	css = "<style>"
	i = 0
	for instruction in exec_q:
		css += "\n" + rule.replace("class_count", str(i+2)).replace("sec", str(i+2))

		i += 1

	return Markup(css + "</style>")

