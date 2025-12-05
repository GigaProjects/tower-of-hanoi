#!/usr/bin/env python3
"""
Tower of Hanoi CLI Game
A command-line implementation of the classic Tower of Hanoi puzzle.
"""

import os
import sys
import tty
import termios


class TowerOfHanoi:
    def __init__(self, num_rings):
        """Initialize the game with the specified number of rings."""
        self.num_rings = num_rings
        self.towers = {
            'A': list(range(num_rings, 0, -1)),  # Start tower with all rings
            'S': [],  # Middle tower (empty)
            'D': []   # Target tower (empty)
        }
        self.target = 'D'
        self.moves = 0
        self.min_moves = (2 ** num_rings) - 1
    
    def getch(self):
        """Read a single character from stdin without echo."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
    
    def clear_screen(self):
        """Clear the terminal screen using ANSI escape codes for seamless refresh."""
        # Move cursor to top-left and clear screen
        print('\033[2J\033[H', end='', flush=True)
    
    def move_cursor(self, row, col):
        """Move cursor to specific position (1-indexed)."""
        print(f'\033[{row};{col}H', end='', flush=True)
    
    def hide_cursor(self):
        """Hide the cursor."""
        print('\033[?25l', end='', flush=True)
    
    def show_cursor(self):
        """Show the cursor."""
        print('\033[?25h', end='', flush=True)
    
    def draw_tower(self, error_msg="", selected_tower=None):
        """Draw the current state of all towers."""
        max_height = self.num_rings
        max_width = self.num_rings * 2 + 1
        
        print("\n")
        print(f"Moves: {self.moves} | Minimum possible: {self.min_moves}")
        print()
        
        # Draw towers from top to bottom
        for level in range(max_height - 1, -1, -1):
            line = "  "
            for tower_name in ['A', 'S', 'D']:
                tower = self.towers[tower_name]
                
                if level < len(tower):
                    ring_size = tower[level]
                    ring = '█' * (ring_size * 2 - 1)
                    padding = (max_width - len(ring)) // 2
                    cell = ' ' * padding + ring + ' ' * padding
                    
                    # Highlight selected ring (top ring of selected tower)
                    is_selected = (selected_tower == tower_name and 
                                   level == len(tower) - 1)
                    
                    if is_selected:
                        # Yellow color for selected ring
                        line += f"\033[93m{cell}\033[0m  "
                    elif tower_name == self.target:
                        # Green color for target tower
                        line += f"\033[92m{cell}\033[0m  "
                    else:
                        line += f"{cell}  "
                else:
                    # Just the pole
                    padding = max_width // 2
                    cell = ' ' * padding + '│' + ' ' * padding
                
                    # Highlight target tower
                    if tower_name == self.target:
                        line += f"\033[92m{cell}\033[0m  "
                    else:
                        line += f"{cell}  "
            
            print(line)
        
        # Draw base
        base_line = "  "
        for tower_name in ['A', 'S', 'D']:
            base = '═' * max_width
            if tower_name == self.target:
                base_line += f"\033[92m{base}\033[0m  "
            else:
                base_line += f"{base}  "
        print(base_line)
        
        # Draw labels
        label_line = "  "
        for tower_name in ['A', 'S', 'D']:
            padding = max_width // 2
            label = ' ' * padding + tower_name + ' ' * padding
            if tower_name == self.target:
                label_line += f"\033[92m{label}\033[0m  "
            else:
                label_line += f"{label}  "
        print(label_line)
        print()
        
        # Print error message in a fixed position if exists
        if error_msg:
            print(f"\033[91m  ⚠ {error_msg}\033[0m")  # Red color for errors
        else:
            print()  # Empty line to keep spacing consistent
    
    def is_valid_move(self, from_tower, to_tower):
        """Check if a move is valid according to Tower of Hanoi rules."""
        # Check if towers exist
        if from_tower not in self.towers or to_tower not in self.towers:
            return False, "Invalid tower selection!"
        
        # Check if moving to the same tower
        if from_tower == to_tower:
            return False, "Cannot move to the same tower!"
        
        # Check if from_tower has rings
        if not self.towers[from_tower]:
            return False, f"Tower {from_tower} is empty!"
        
        # Check if we can place the ring (smaller on larger)
        if self.towers[to_tower]:
            if self.towers[from_tower][-1] > self.towers[to_tower][-1]:
                return False, "Cannot place a larger ring on a smaller ring!"
        
        return True, ""
    
    def move_ring(self, from_tower, to_tower):
        """Move a ring from one tower to another."""
        valid, error_msg = self.is_valid_move(from_tower, to_tower)
        
        if not valid:
            return False, error_msg
        
        # Perform the move
        ring = self.towers[from_tower].pop()
        self.towers[to_tower].append(ring)
        self.moves += 1
        
        return True, f"Moved ring {ring} from {from_tower} to {to_tower}"
    
    def is_won(self):
        """Check if the game is won."""
        return len(self.towers[self.target]) == self.num_rings
    
    def play(self):
        """Main game loop."""
        error_msg = ""
        
        while True:
            self.clear_screen()
            
            # Check win condition first
            if self.is_won():
                self.draw_tower()
                print(f"CONGRATULATIONS! You won in {self.moves} moves!")
                if self.moves == self.min_moves:
                    print("PERFECT! You solved it in the minimum number of moves!")
                else:
                    print(f"The minimum possible was {self.min_moves} moves.")
                break
            
            # Initialize selected_tower for this iteration
            selected_tower = None
            
            # Draw towers with any error message
            self.draw_tower(error_msg, selected_tower)
            error_msg = ""  # Clear error for next iteration
            
            # Get user input - simplified prompt
            print("  Your move: ", end='', flush=True)
            
            # Read characters one by one
            user_input = ""
            selected_tower = None
            
            while True:
                char = self.getch()
                
                # Handle Ctrl+C
                if char == '\x03':  # Ctrl+C
                    raise KeyboardInterrupt
                
                # Handle backspace (both DEL and BACKSPACE)
                if char in ['\x7f', '\x08']:
                    if len(user_input) > 0:
                        user_input = user_input[:-1]
                        selected_tower = None
                        # Redraw without selection
                        self.clear_screen()
                        self.draw_tower(error_msg)
                        print("  Your move: " + user_input, end='', flush=True)
                    continue
                
                char = char.upper()
                
                # Handle special single-character commands
                if char in ['Q', 'R']:
                    print(char)
                    user_input = char
                    break
                
                # For two-character commands (tower moves)
                if char in ['A', 'S', 'D']:
                    print(char, end='', flush=True)
                    user_input += char
                    
                    # After first character, redraw with selection
                    if len(user_input) == 1:
                        selected_tower = char
                        # Check if tower has rings
                        if self.towers[selected_tower]:
                            self.clear_screen()
                            self.draw_tower(error_msg, selected_tower)
                            print("  Your move: " + user_input, end='', flush=True)
                    
                    if len(user_input) == 2:
                        print()  # New line after second character
                        break
            
            # Process the input
            if user_input == 'Q':
                print("\nThanks for playing! Goodbye!\n")
                break
            elif user_input == 'R':
                return True  # Signal to restart
            elif len(user_input) == 2:
                from_tower = user_input[0]
                to_tower = user_input[1]
                
                success, message = self.move_ring(from_tower, to_tower)
                
                if not success:
                    error_msg = message
            else:
                error_msg = "Invalid input!"
        
        return False  # Don't restart


def select_difficulty():
    """Let the user select the number of rings."""
    os.system('clear' if os.name != 'nt' else 'cls')    
    print(f"""
▀▛▘                ▗▀▖ ▌ ▌         ▗ 
 ▌▞▀▖▌  ▌▞▀▖▙▀▖ ▞▀▖▐   ▙▄▌▝▀▖▛▀▖▞▀▖▄ 
 ▌▌ ▌▐▐▐ ▛▀ ▌   ▌ ▌▜▀  ▌ ▌▞▀▌▌ ▌▌ ▌▐ 
 ▘▝▀  ▘▘ ▝▀▘▘   ▝▀ ▐   ▘ ▘▝▀▘▘ ▘▝▀ ▀▘
    """)   
    print("A classic puzzle game: Move all rings from Tower A to Tower D")
    print()
    print("Rules:")
    print("  • Only one ring can be moved at a time")
    print("  • A ring can only be placed on top of a larger ring")
    print("  • You can use Tower S as an auxiliary tower")
    print()
    print()
    
    while True:
        try:
            num_rings = int(input("Select number of rings (1-10): ").strip())
            if 1 <= num_rings <= 10:
                return num_rings
            else:
                print("Please enter a number between 1 and 10.")
        except ValueError:
            print("Please enter a valid number.")
        except KeyboardInterrupt:
            print("\n\nGoodbye!\n")
            sys.exit(0)


def main():
    """Main function to run the game."""
    try:
        while True:
            num_rings = select_difficulty()
            game = TowerOfHanoi(num_rings)
            restart = game.play()
            
            if not restart:
                break
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Goodbye!\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
