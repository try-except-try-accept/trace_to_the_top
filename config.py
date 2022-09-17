SPACE4 = " "*4
SPACE_SIZE = 4
MAX_CELL_LENGTH = 50
CONTROL_STATEMENTS = 'if,elif,else,while,def,for,try,except'.split(",")
REMOVE_VARS = ["_this_func", "_params", "_namespace", "_inputs"]  # helpers for identifying scope

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