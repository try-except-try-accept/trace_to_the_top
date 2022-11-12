SPACE4 = " "*4
SPACE_SIZE = 4
MAX_CELL_LENGTH = 50
CONTROL_STATEMENTS = 'if,elif,else,while,def,for,try,except'.split(",")
REMOVE_VARS = ["_input_as_print", "_this_func", "_params", "_namespace", "_inputs", "_code"]  # helpers for identifying scope
PRINT_INPUT_DEC = "!@#$@###"
SYMBOL_REPS = {">":"$gt",
            "<":"$lt",
            "!=":"$ineq",
            "==":"$eq",
            "+":"$add",
            "-": "$sub",
            "*": "$mul",
            "/": "$div",
            "%": "$mod",
            "(": "$oprb",
            ")": "$clrb",
            "[": "$opsb",
            "]": "$clsb"}