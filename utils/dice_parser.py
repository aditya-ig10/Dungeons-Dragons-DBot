# utils/dice_parser.py
import re
import random

def parse_and_roll(notation):
    details = []
    def replace_dice(match):
        n = int(match.group(1))
        sides = int(match.group(2))
        keep_type = match.group(3)
        keep_num = match.group(4)
        if keep_num:
            keep_num = int(keep_num)
        else:
            if keep_type:
                raise ValueError("Keep number required")
        if keep_type and keep_num > n:
            raise ValueError("Keep number exceeds dice count")
        rolls = [random.randint(1, sides) for _ in range(n)]
        original_rolls = rolls.copy()
        if keep_type:
            if keep_type == 'kh':
                rolls = sorted(rolls, reverse=True)[:keep_num]
            elif keep_type == 'kl':
                rolls = sorted(rolls)[:keep_num]
            else:
                raise ValueError("Invalid keep type")
        total = sum(rolls)
        details.append({
            'expression': match.group(0),
            'rolls': original_rolls,
            'kept': rolls if keep_type else original_rolls,
            'total': total
        })
        return str(total)
    dice_re = re.compile(r'(\d+)d(\d+)(kh|kl)?(\d+)?', re.IGNORECASE)
    new_notation = dice_re.sub(replace_dice, notation)
    try:
        result = eval(new_notation, {"__builtins__": {}}, {})
    except:
        raise ValueError("Invalid dice notation")
    return result, details