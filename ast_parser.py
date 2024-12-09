class ASTNode:
    def __init__(self, node_type, value=None):
        self.node_type = node_type
        self.value = value
        self.children = []

    def add_child(self, child):
        self.children.append(child)

class AST_Parser:
    def __init__(self, tokens):
        self.tokens = tokens
        self.current_index = 0
    
    def transition(self, state, token_type):
        # Transition function δ(state, token)
        if state == 'S0':
            if token_type == 'NOTE':
                return 'S1'
            elif token_type == 'CHORD':
                return 'S3' 
            elif token_type in ['SHARE', 'PLAY', 'SAVE']:
                return 'S5'
        elif state == 'S1':
            if token_type == 'DURATION':
                return 'S2'
        elif state == 'S2':
            if token_type == 'NOTE':
                return 'S1'
            elif token_type == 'TEMPO':
                return 'S4'
            elif token_type == 'CHORD':
                return 'S3'
        elif state == 'S3':
            if token_type == 'DURATION':
                return 'S2'
            elif token_type == 'NOTE':
                return 'S3'
        elif state == 'S4':
            if token_type == 'NOTE':
                return 'S1'
            elif token_type == 'CHORD':
                return 'S3'
            elif token_type in ['SHARE', 'PLAY', 'SAVE']:
                return 'S5'
        elif state == 'S5':
            if token_type in ['SHARE', 'PLAY', 'SAVE']:
                return 'S5'
        return 'Serr'

    def parse(self):
        root = ASTNode("S")  # Start symbol
        self.current_state = 'S0'
        
        composition_node = self.parse_composition()
        if composition_node:
            root.add_child(composition_node)
        
        # Parse the Command part of the grammar
        command_node = self.parse_command()
        if self.current_state != 'S5':
            raise ValueError("Incorrect token sequence: Expected a command (PLAY, SHARE, or SAVE) after composition")
        root.add_child(command_node)
        
        # Check for completeness
        if self.current_index != len(self.tokens):
            raise ValueError("Parsing error: Extra tokens found after command")
        
        return root

    def parse_composition(self):
        # Composition -> (Sequence Tempo)+ | ε
        composition_node = ASTNode("Composition")
        while self.current_index < len(self.tokens):
            # Parse a sequence
            sequence_node = self.parse_sequence()
            if sequence_node:
                composition_node.add_child(sequence_node)
            else:
                break

            # Ensure a tempo follows the sequence
            if self.current_index >= len(self.tokens):
                raise ValueError("Parsing error: Expected a TEMPO after sequence")
            
            self.current_state = self.transition(self.current_state, self.tokens[self.current_index][0])
            if self.current_state == 'Serr':
                raise ValueError("Parsing error: Expected a TEMPO after sequence")
            
            composition_node.add_child(self.parse_tempo())

        return composition_node


    def parse_sequence(self):
        # Sequence -> Element Sequence | Element
        sequence_node = ASTNode("Sequence")
        if self.match("SHARE") or self.match("PLAY") or self.match("SAVE"):
            return None
        elif not(self.match("NOTE") or self.match("CHORD")):
            raise ValueError("Invalid Composition")
        while self.match("NOTE") or self.match("CHORD"):
            print(self.tokens[self.current_index][0])
            print(self.current_state)
            expected_state = self.transition(self.current_state, self.tokens[self.current_index][0])
            if expected_state == 'Serr':
                raise ValueError(f"Incorrect sequence at '{self.tokens[self.current_index][1]}'")

            element_node = self.parse_element()
            if element_node:
                sequence_node.add_child(element_node)

        return sequence_node

    def parse_element(self):
        element_node = ASTNode("Element")
        self.current_state = self.transition(self.current_state, self.tokens[self.current_index][0])
        if self.current_state == 'Serr':
            raise ValueError(f"Incorrect sequence at '{self.tokens[self.current_index][1]}'")
        if self.match("NOTE"):
            element_node.add_child(self.parse_note_element())
        elif self.match("CHORD"):
            element_node.add_child(self.parse_chord_element())
        else:
            raise ValueError(f"Incorrect sequence at '{self.tokens[self.current_index][1]}'")
        
        return element_node

    def parse_note_element(self):
        # NoteElement -> Note Duration
        note_element_node = ASTNode("NoteElement")
        note_element_node.add_child(ASTNode("Note", self.consume("NOTE")))

        if self.current_index >= len(self.tokens):
            raise ValueError("Incorrect sequence: Each note should be immediately followed by its duration")
        
        self.current_state = self.transition(self.current_state, self.tokens[self.current_index][0])
        if self.current_state == 'Serr':
            raise ValueError("Incorrect sequence: Each note should be immediately followed by its duration")
        
        note_element_node.add_child(self.parse_duration())
        return note_element_node
    
    def parse_chord_element(self):
        # ChordElement -> Chord (ChordNotes) Duration
        chord_element_node = ASTNode("ChordElement")
        chord_token = self.consume("CHORD")
        
        chord_keyword, chord_notes = chord_token.split(" ", 1)
        chord_notes = chord_notes.strip("()")
        
        chord_element_node.add_child(ASTNode("Chord", chord_keyword))
        chord_element_node.add_child(ASTNode("LeftParen", "("))
        
        chord_notes_node = ASTNode("ChordNotes")
        for note in chord_notes.split():
            chord_notes_node.add_child(ASTNode("Note", note))
        
        chord_element_node.add_child(chord_notes_node)
        chord_element_node.add_child(ASTNode("RightParen", ")"))
        
        if self.current_index >= len(self.tokens):
            raise ValueError("Incorrect sequence: Each chord should be immediately followed by its duration")

        self.current_state = self.transition(self.current_state, self.tokens[self.current_index][0])
        if self.current_state == 'Serr':
            raise ValueError("Incorrect sequence: Each chord should be immediately followed by its duration")
        
        chord_element_node.add_child(self.parse_duration())
        return chord_element_node

    def parse_command(self):
        command_node = ASTNode("Command")
        while self.match("PLAY") or self.match("SHARE") or self.match("SAVE"):
            command_token = self.tokens[self.current_index][0]
            expected_state = self.transition(self.current_state, command_token)
            if expected_state == 'Serr':
                raise ValueError(f"Incorrect command at '{self.tokens[self.current_index][1]}'")
            command_node.add_child(ASTNode("CommandAction", self.consume(command_token)))
            self.current_state = expected_state
        
        return command_node

    def parse_duration(self):
        return ASTNode("Duration", self.consume("DURATION"))

    def parse_tempo(self):
        return ASTNode("Tempo", self.consume("TEMPO"))

    def match(self, expected_type):
        if self.current_index < len(self.tokens):
            return self.tokens[self.current_index][0] == expected_type
        return False

    def consume(self, expected_type):
        if self.match(expected_type):
            token_value = self.tokens[self.current_index][1]
            self.current_index += 1
            return token_value
        else:
            raise ValueError(f"Expected token {expected_type}, but got {self.tokens[self.current_index][0]}")

    def print_ast(self, node, level=0):
        print(" " * level * 2 + f"{node.node_type}: {node.value if node.value else ''}")
        for child in node.children:
            self.print_ast(child, level + 1)
