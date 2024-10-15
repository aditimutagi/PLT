class MusicLangScanner:
    def __init__(self, code):
        self.code = code
        self.tokens = []
        self.current_index = 0

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

            # Handle chords with multiple notes
            if token.startswith('chord'):
                chord_token = token
                while (self.current_index < len(self.code) and 
                       not self.is_whitespace(self.code[self.current_index]) and 
                       self.code[self.current_index] != ','):
                    self.current_index += 1
                chord_notes = self.code[token_start:self.current_index].strip()
                self.tokens.append(('CHORD', chord_notes))
                continue

            # Check if the token represents an action, note, or duration
            token_type = (
                self.is_share(token) or
                self.is_play(token) or
                self.is_duration(token) or
                self.is_note_or_chord(token)
            )

            if token_type:
                self.tokens.append((token_type, token))
                
        # Tempo inference logic in the scan function
        if len(self.tokens) > 1:
            last_token = self.tokens[-1]
            second_to_last_token = self.tokens[-2]

            if self.is_duration(last_token[1]):
                tempo_token = self.tokens.pop()
                self.tokens.append(('TEMPO', tempo_token[1]))  

            elif last_token[1] == 'share' and self.is_duration(second_to_last_token[1]):
                self.tokens[-2] = (('TEMPO', second_to_last_token[1]))  
            
            else:
                print("ERROR!")

        return self.tokens



if __name__ == "__main__":
    code = "play C4 1.0 D4 0.5 E4 0.75 chord C4 D4 0.75 1.5 2.5 share" # sample command
    scanner = MusicLangScanner(code)
    tokens = scanner.scan()
    for token in tokens:
        print(f"<{token[0]}, {token[1]}>")