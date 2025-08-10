"""
Dice parsing and rolling utilities for D&D-style dice notation
"""
import re
import random
from typing import Dict, List, Tuple

class DiceParser:
    """Parse and roll dice using D&D notation"""
    
    def __init__(self):
        # Regex pattern for dice notation: XdY+Z, XdYkH, XdYkL, etc.
        self.dice_pattern = re.compile(
            r'(\d+)?d(\d+)(?:(k[hl])(\d+))?(?:([+\-*/])(\d+))?',
            re.IGNORECASE
        )
        self.simple_pattern = re.compile(r'^(\d+)$')
    
    def parse_and_roll(self, dice_string: str) -> Dict:
        """
        Parse dice string and return roll results
        
        Supported formats:
        - 1d20: Roll one 20-sided die
        - 2d6+3: Roll two 6-sided dice and add 3
        - 4d6kh3: Roll four 6-sided dice, keep highest 3
        - 4d6kl1: Roll four 6-sided dice, keep lowest 1
        - 1d8*2: Roll one 8-sided die and multiply by 2
        """
        dice_string = dice_string.strip().lower().replace(' ', '')
        
        # Check for simple number
        simple_match = self.simple_pattern.match(dice_string)
        if simple_match:
            value = int(simple_match.group(1))
            return {
                'total': value,
                'details': f'Static value: {value}'
            }
        
        # Parse dice notation
        match = self.dice_pattern.match(dice_string)
        if not match:
            raise ValueError("Invalid dice format. Use formats like: 1d20, 2d6+3, 4d6kh3")
        
        # Extract components
        num_dice = int(match.group(1)) if match.group(1) else 1
        die_size = int(match.group(2))
        keep_type = match.group(3)  # kh or kl
        keep_count = int(match.group(4)) if match.group(4) else None
        operator = match.group(5)
        modifier = int(match.group(6)) if match.group(6) else 0
        
        # Validation
        if num_dice <= 0 or num_dice > 100:
            raise ValueError("Number of dice must be between 1 and 100")
        if die_size <= 0 or die_size > 1000:
            raise ValueError("Die size must be between 1 and 1000")
        if keep_count and (keep_count <= 0 or keep_count > num_dice):
            raise ValueError("Keep count must be between 1 and number of dice")
        
        # Roll dice
        rolls = [random.randint(1, die_size) for _ in range(num_dice)]
        
        # Apply keep highest/lowest
        if keep_type and keep_count:
            if keep_type == 'kh':  # keep highest
                kept_rolls = sorted(rolls, reverse=True)[:keep_count]
            else:  # keep lowest
                kept_rolls = sorted(rolls)[:keep_count]
            
            # Format details
            all_rolls_str = ', '.join(map(str, rolls))
            kept_rolls_str = ', '.join(map(str, kept_rolls))
            details = f"Rolled: [{all_rolls_str}] → Kept: [{kept_rolls_str}]"
        else:
            kept_rolls = rolls
            details = f"Rolled: [{', '.join(map(str, rolls))}]"
        
        # Calculate base total
        total = sum(kept_rolls)
        
        # Apply modifier
        if operator and modifier:
            if operator == '+':
                total += modifier
                details += f" + {modifier}"
            elif operator == '-':
                total -= modifier
                details += f" - {modifier}"
            elif operator == '*':
                total *= modifier
                details += f" × {modifier}"
            elif operator == '/':
                total = int(total / modifier)
                details += f" ÷ {modifier}"
        
        return {
            'total': total,
            'details': details
        }
    
    def roll_multiple(self, dice_expressions: List[str]) -> Dict:
        """Roll multiple dice expressions and sum them"""
        results = []
        total = 0
        
        for expression in dice_expressions:
            result = self.parse_and_roll(expression)
            results.append(result)
            total += result['total']
        
        details = ' + '.join([f"({r['details']} = {r['total']})" for r in results])
        
        return {
            'total': total,
            'details': details,
            'individual_results': results
        }

# Example usage and testing
if __name__ == "__main__":
    parser = DiceParser()
    
    # Test various dice formats
    test_cases = [
        "1d20",
        "2d6+3",
        "4d6kh3",
        "1d8*2",
        "3d6-1",
        "20"  # Simple number
    ]
    
    for test in test_cases:
        try:
            result = parser.parse_and_roll(test)
            print(f"{test}: {result['total']} ({result['details']})")
        except Exception as e:
            print(f"{test}: Error - {e}")
