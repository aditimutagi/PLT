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

    def parse(self):
        root = ASTNode("S")  # Start symbol
        composition_node = self.parse_composition()
        if composition_node:
            root.add_child(composition_node)
        
        # Parse the Command part of the grammar
        command_node = self.parse_command()
        if not command_node:
            raise ValueError("Expected a command (PLAY, SHARE, or SAVE) after composition")
        
        root.add_child(command_node)
        
        # Check for completeness
        if self.current_index != len(self.tokens):
            raise ValueError("Extra tokens found after command")
        
        return root

    def parse_composition(self):
        # Composition -> Sequence Tempo | ε
        composition_node = ASTNode("Composition")
        sequence_node = self.parse_sequence()
        
        if sequence_node:
            composition_node.add_child(sequence_node)
            if not self.match("TEMPO"):
                raise ValueError("Expected a TEMPO after sequence")
            composition_node.add_child(self.parse_tempo())
        
        return composition_node

    def parse_sequence(self):
        # Sequence -> Element Sequence | Element
        sequence_node = ASTNode("Sequence")
        element_node = self.parse_element()
        
        if not element_node:
            return None
        
        sequence_node.add_child(element_node)
        
        # Add any additional elements recursively
        while self.match("NOTE") or self.match("CHORD"):
            sequence_node.add_child(self.parse_element())
        
        return sequence_node

    def parse_element(self):
        element_node = ASTNode("Element")
        if self.match("NOTE"):
            element_node.add_child(self.parse_note_element())
        elif self.match("CHORD"):
            element_node.add_child(self.parse_chord_element())
        else:
            return None  # Not an Element
        
        return element_node

    def parse_chord_element(self):
        # ChordElement -> Chord (ChordNotes) Duration
        chord_element_node = ASTNode("ChordElement")
        chord_token = self.consume("CHORD")
        
        chord_keyword, chord_notes = chord_token.split(" ", 1)
        chord_notes = chord_notes.strip("()")
        
        chord_element_node.add_child(ASTNode("Chord", chord_keyword))
        chord_element_node.add_child(ASTNode("LeftParen", "("))
        
        # Parse ChordNotes
        chord_notes_node = ASTNode("ChordNotes")
        for note in chord_notes.split():
            chord_notes_node.add_child(ASTNode("Note", note))
        
        chord_element_node.add_child(chord_notes_node)
        chord_element_node.add_child(ASTNode("RightParen", ")"))
        
        if not self.match("DURATION"):
            raise ValueError("Rejected: Chords must be followed by specified duration")
        
        chord_element_node.add_child(self.parse_duration())
        return chord_element_node

    def parse_note_element(self):
        # NoteElement -> Note Duration
        note_element_node = ASTNode("NoteElement")
        note_element_node.add_child(ASTNode("Note", self.consume("NOTE")))
        
        if not self.match("DURATION"):
            raise ValueError("Each note should be immediately followed by its duration")
        
        note_element_node.add_child(self.parse_duration())
        return note_element_node

    def parse_duration(self):
        return ASTNode("Duration", self.consume("DURATION"))

    def parse_tempo(self):
        return ASTNode("Tempo", self.consume("TEMPO"))

    def parse_command(self):
        # Command -> CommandAction Command
        command_node = ASTNode("Command")
        while self.match("PLAY") or self.match("SHARE") or self.match("SAVE"):
            command_node.add_child(ASTNode("CommandAction", self.consume(self.tokens[self.current_index][0])))
        if len(command_node.children) == 0:
            return None
        return command_node

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