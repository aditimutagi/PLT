import sys
from ast_parser import AST_Parser, ASTProcessor
from lower_level_to_midi import MIDI_LowerLevel

class MusicLangScanner:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_index = 0

    def is_whitespace(self, char):
        return char in (' ', '\t', '\n')

    def is_note_or_chord(self, token):
        note_pattern = 'ABCDEFG'
        if token == 'chord':
            return 'CHORD'
        if len(token) > 2 and token[1] in ('#', 'b') and token[0] in note_pattern and token[2].isdigit():
            return 'NOTE'
        elif len(token) == 2 and token[0] in note_pattern and token[1].isdigit():
            return 'NOTE'
        return None

    def is_duration(self, token):
        try:
            value = float(token)
            if '.' in token and value >= 0:
                return 'DURATION'
            return None
        except ValueError:
            return None

    def is_tempo(self, token):
        try:
            value = int(token)
            return 'TEMPO' if value >= 0 else None
        except ValueError:
            return None

    def is_play(self, token):
        if token in 'play':
            return 'PLAY'
        return None
    
    def is_share(self, token):
        if token in 'share':
            return 'SHARE'
        return None

    def is_save(self, token):
        if token in 'save':
            return 'SAVE'
        return None

    def scan(self):
        state = 'S0'

        while self.current_index < len(self.code):
            char = self.code[self.current_index]

            if self.is_whitespace(char):
                self.current_index += 1
                continue

            # Start reading a token
            token_start = self.current_index
            while (self.current_index < len(self.code) and
                   not self.is_whitespace(self.code[self.current_index]) and
                   self.code[self.current_index] != ','):
                self.current_index += 1

            token = self.code[token_start:self.current_index].strip()

            # Handle chords : must be formatted as "chord (note note note...)"
            if token == 'chord':
                self.current_index += 1
                # Check for opening parenthesis
                if self.current_index < len(self.code) and self.code[self.current_index] == '(':
                    self.current_index += 1
                    notes = []
                    while self.current_index < len(self.code):
                        # Check if we have reached the closing parenthesis
                        if self.code[self.current_index] == ')':
                            self.current_index += 1
                            break
                        
                        # Extract a potential note
                        note_start = self.current_index
                        while (self.current_index < len(self.code) and 
                            not self.is_whitespace(self.code[self.current_index]) and 
                            self.code[self.current_index] != ',' and
                            self.code[self.current_index] != ')'):  # Include check for closing parenthesis
                            self.current_index += 1

                        # Validate and add note
                        note = self.code[note_start:self.current_index].strip()
                        if self.is_note_or_chord(note) == 'NOTE':
                            notes.append(note)
                        else:
                            raise ValueError(f"Rejected: Invalid note '{note}' in chord")
                            
                        # Handle optional whitespace and commas
                        while self.current_index < len(self.code) and (self.is_whitespace(self.code[self.current_index]) or self.code[self.current_index] == ','):
                            self.current_index += 1
                    
                    # Check if we exited the loop with a closing parenthesis
                    if self.code[self.current_index - 1] != ')':
                        raise ValueError("Rejected: Missing closing parenthesis for chord")

                    # Check if there are valid notes inside the chord
                    if len(notes) > 0:
                        chord_format = f"chord ({' '.join(notes)})"
                        self.tokens.append(('CHORD', chord_format))
                        token_type = 'CHORD'
                    else:
                        raise ValueError("Rejected: Missing notes in chord")

                else:
                    raise ValueError("Rejected: Missing opening parenthesis for chord")

            else:
                # Check if the token represents an action, note, or duration
                token_type = (
                    self.is_share(token) or
                    self.is_play(token) or
                    self.is_duration(token) or
                    self.is_tempo(token) or
                    self.is_note_or_chord(token) or
                    self.is_save(token)
                )
                self.tokens.append((token_type, token))

            if token_type == None:
                raise ValueError(f"Rejected: Invalid token '{token}'")
            
            

        return "Tokens accepted by scanner \n", self.tokens

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scanner.py <music_code>")
        sys.exit(1)

    code = sys.argv[1]
    
    try:
        scanner = MusicLangScanner(code)
        message, tokens = scanner.scan()
        for token in tokens:
            print(f"<{token[0]}, {token[1]}>")
        print(message)

        if "accepted" in message:
            # Pass tokens to the parser
            parser = AST_Parser(tokens)
            try:
                ast = parser.parse()
                print("Generated AST:")
                parser.print_ast(ast)

                processor = ASTProcessor(ast)
                lower_level_output = processor.process()
                print("\nGenerated Lower-Level Language Output:")
                print(lower_level_output)

                midi_gen = MIDI_LowerLevel()
                command = midi_gen.handle_command(lower_level_output)

            except ValueError as e:
                print("Parsing ValueError:\n", e, "\n")
    except ValueError as e:
        print("Scanner ValueError:\n", e)
        print("Cannot parse: input rejected by scanner.\n")
