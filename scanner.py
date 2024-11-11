import sys
from ast_parser import AST_Parser

class MusicLangScanner:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_index = 0
    
    def transition(self, state, token_type):
        # Transition function δ(state, token)
        if state == 'S0':
            if token_type == 'NOTE':
                return 'S1'
            elif token_type == 'CHORD':
                return 'S3' 
            elif token_type == 'SHARE':
                return 'S4'
            elif token_type == 'SAVE':
                return 'S4'
            elif token_type == 'PLAY':
                return 'S4'
        elif state == 'S1':
            if token_type == 'DURATION':
                return 'S2'
        elif state == 'S2':
            if token_type == 'NOTE':
                return 'S1'
            elif token_type == 'DURATION': # TEMPO
                return 'S4'
            elif token_type == 'CHORD':
                return 'S3'
        elif state == 'S3':
            if token_type == 'DURATION':
                return 'S2'
            elif token_type == 'NOTE':
                return 'S3'
        elif state == 'S4':
            if token_type == 'SHARE':
                return 'S4'
            elif token_type == 'PLAY':
                return 'S4'
            elif token_type == 'SAVE':
                return 'S4'
        # If no valid transition found, go to error state
        return 'Serr'


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
            return 'DURATION' if value >= 0 else None
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

            # Handle chords 
            if token == 'chord':
                self.current_index += 1
                # Check for opening parenthesis
                if self.current_index < len(self.code) and self.code[self.current_index] == '(':
                    self.current_index += 1
                    notes = []
                    while self.current_index < len(self.code):
                        # Break if we reach the closing parenthesis
                        if self.code[self.current_index] == ')':
                            self.current_index += 1
                            break
                        
                        note_start = self.current_index
                        while (self.current_index < len(self.code) and 
                            not self.is_whitespace(self.code[self.current_index]) and 
                            self.code[self.current_index] != ',' and
                            self.code[self.current_index] != ')'):  # Include check for closing parenthesis
                            self.current_index += 1

                        note = self.code[note_start:self.current_index].strip()
                        if self.is_note_or_chord(note) == 'NOTE':
                            notes.append(note)
                        else:
                            return f"Rejected: Invalid note '{note}' in chord", self.tokens
                            
                        # Handle optional whitespace and commas
                        while self.current_index < len(self.code) and (self.is_whitespace(self.code[self.current_index]) or self.code[self.current_index] == ','):
                            self.current_index += 1
                    
                    # Check if we exited the loop due to reaching the closing parenthesis
                    if len(notes) > 0:
                        self.tokens.append(('CHORD', token + " (" + ' '.join(notes) + ")"))
                        token_type = 'CHORD'
                    else:
                        return f"Rejected: Missing notes in chord", self.tokens

                else:
                    return f"Rejected: Missing opening parenthesis for chord", self.tokens

            else:
                # Check if the token represents an action, note, or duration
                token_type = (
                    self.is_share(token) or
                    self.is_play(token) or
                    self.is_duration(token) or
                    self.is_note_or_chord(token) or
                    self.is_save(token)
                )

            if token_type == None:
                return f"Rejected: Invalid token '{token}'", self.tokens
            
            # Perform state transition based on the token type
            new_state = self.transition(state, token_type)
            if new_state == 'Serr':
                return f"Rejected: Invalid token sequence at '{token}'", self.tokens

            state = new_state
            if state == 'S4' and token_type == 'DURATION': # means two durations --> tempo provided
                self.tokens.append(('TEMPO', token))
            elif token_type != 'CHORD':
                self.tokens.append((token_type, token))

        # Check if the final state is an accepting state
        if state == 'S4':
            return "Accepted", self.tokens
        elif state == 'S1':
            return "Rejected: Each note should be immediately followed by its duration", self.tokens
        elif state == 'S2':
            return "Rejected: Must provide the duration for each note/chord and overall tempo", self.tokens
        elif state == 'S3':
            return "Rejected: Chords must be followed by list of notes and specified duration", self.tokens
        else:
            return "Rejected: Incomplete or incorrect input sequence", self.tokens
        
        
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 scanner.py <music_code>")
        sys.exit(1)

    code = sys.argv[1]
    
    scanner = MusicLangScanner(code)
    message, tokens = scanner.scan()
    for token in tokens:
        print(f"<{token[0]}, {token[1]}>")
    print(message)

    if message == "Accepted":
        # Pass tokens to the parser
        parser = AST_Parser(tokens)
        ast = parser.parse()
        print("Generated AST:")
        parser.print_ast(ast)
    else:
        print("Cannot parse; input rejected by scanner.")