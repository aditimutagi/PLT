class MusicLangScanner:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_index = 0
    
    def transition(self, state, token_type):
        # Transition function δ(state, token)
        if state == 'S0':
            if token_type == 'PLAY':
                return 'S1'
            elif token_type == 'NOTE':
                return 'S2'
            elif token_type == 'CHORD':
                return 'S4'
            elif token_type == 'SHARE':
                return 'S5'
        elif state == 'S1':
            if token_type == 'NOTE':
                return 'S2'
            elif token_type == 'CHORD':
                return 'S4'
        elif state == 'S2':
            if token_type == 'DURATION':
                return 'S3'
        elif state == 'S3':
            if token_type == 'NOTE':
                return 'S2'
            elif token_type == 'DURATION': # TEMPO
                return 'S5'
            elif token_type == 'CHORD':
                return 'S4'
        elif state == 'S4':
            if token_type == 'NOTE':
                return 'S2'
            if token_type == 'DURATION':
                return 'S3'
        elif state == 'S5':
            if token_type == 'NOTE':
                return 'S2'
            elif token_type == 'CHORD':
                return 'S4'
            if token_type == 'SHARE':
                return 'S5'
        # If no valid transition found, go to error state
        return 'Serr'


    def is_whitespace(self, char):
        return char in (' ', '\t', '\n')

    def is_note_or_chord(self, token):
        note_pattern = 'ABCDEFG'
        if token.startswith('chord'):
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

            # Handle chords with parentheses
            if token.startswith('chord'):
                self.current_index += 1
                chord_token = token
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
                            print(f"ERROR: Invalid note '{note}' in chord")
                            return []
                            
                        # Handle optional whitespace and commas
                        while self.current_index < len(self.code) and (self.is_whitespace(self.code[self.current_index]) or self.code[self.current_index] == ','):
                            self.current_index += 1
                    
                    # Check if we exited the loop due to reaching the closing parenthesis
                    if len(notes) > 0:
                        self.tokens.append(('CHORD', ' '.join(notes)))
                        token_type = 'CHORD'
                    else:
                        print("ERROR: Missing notes in chord")
                        return []

                else:
                    print("ERROR: Missing opening parenthesis for chord")
                    return []

            else:
                # Check if the token represents an action, note, or duration
                token_type = (
                    self.is_share(token) or
                    self.is_play(token) or
                    self.is_duration(token) or
                    self.is_note_or_chord(token)
                )

            # Perform state transition based on the token type
            new_state = self.transition(state, token_type)
            if new_state == 'Serr':
                print(f"ERROR: Invalid token sequence at '{token}'")
                return []  # Return an empty list if an error occurs
            # Update the state and add the token to the list
            state = new_state
            if state == 'S5' and token_type == 'DURATION': # means two durations --> tempo provided
                self.tokens.append(('TEMPO', token))
            else:
                self.tokens.append((token_type, token))

        # Check if the final state is an accepting state
        if state in {'S5'}:
            print("Accepted")
        else:
            print("Rejected")
        
        return self.tokens



if __name__ == "__main__":
    code = "play C4 1.0 D4 0.5 E4 0.75 chord (C4 D4) 0.75 130 share" # sample command
    scanner = MusicLangScanner(code)
    tokens = scanner.scan()
    for token in tokens:
        print(f"<{token[0]}, {token[1]}>")