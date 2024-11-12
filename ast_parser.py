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
        root = self.parse_composition()
        if root and self.current_index == len(self.tokens):
            return root
        else:
            raise ValueError("Parsing error: incomplete or incorrect input")

    def parse_composition(self):
        composition_node = ASTNode("Composition")
        if self.match("CHORD") or self.match("NOTE"):
            composition_node.add_child(self.parse_sequence())
        if self.match("TEMPO"):
            composition_node.add_child(self.parse_tempo())
        else:
            raise ValueError("Expected a tempo after the sequence")
        if self.match("PLAY") or self.match("SHARE") or self.match("SAVE"):
            composition_node.add_child(self.parse_command())
        return composition_node

    def parse_sequence(self):
        sequence_node = ASTNode("Sequence")
        while self.match("CHORD") or self.match("NOTE"):
            sequence_node.add_child(self.parse_element())
        return sequence_node

    def parse_element(self):
        element_node = ASTNode("Element")
        if self.match("CHORD"):
            element_node.add_child(self.parse_chord_element())
        elif self.match("NOTE"):
            element_node.add_child(self.parse_note_element())
        return element_node

    def parse_chord_element(self):
        chord_element_node = ASTNode("ChordElement")
    
        chord_token = self.consume("CHORD")
        chord_keyword, chord_notes = chord_token.split(" ", 1)  # chord_keyword is "chord", chord_notes is "(D3 C5)"
        chord_notes = chord_notes.strip("()")
        
        chord_element_node.add_child(ASTNode("Chord", chord_keyword))
        chord_element_node.add_child(ASTNode("LeftParen", "("))
        chord_element_node.add_child(ASTNode("ChordNotes", chord_notes))
        chord_element_node.add_child(ASTNode("RightParen", ")"))
        
        if not self.match("DURATION"):
            raise ValueError("Rejected: Chords must be followed by list of notes and specified duration")
        
        chord_element_node.add_child(self.parse_duration())
        return chord_element_node

    def parse_note_element(self):
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
        command_node = ASTNode("Command")
        while self.match("PLAY") or self.match("SHARE") or self.match("SAVE"):
            command_node.add_child(ASTNode("CommandAction", self.consume(self.tokens[self.current_index][0])))
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
