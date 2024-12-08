class ASTProcessor:
    def __init__(self, ast):
        self.ast = ast
        self.output = []

    def process(self):
        self.visit_node(self.ast)
        return "\n".join(self.output)

    def visit_node(self, node):
        if node.node_type == "NoteElement":
            self.process_note_element(node)
        elif node.node_type == "ChordElement":
            self.process_chord_element(node)
        elif node.node_type == "Tempo":
            self.process_tempo(node)
        elif node.node_type == "CommandAction":
            self.process_command(node)
        else:
            for child in node.children:
                self.visit_node(child)

    def process_note_element(self, node):
        note = None
        duration = None
        for child in node.children:
            if child.node_type == "Note":
                note = self.note_to_midi(child.value)
            elif child.node_type == "Duration":
                duration = float(child.value)
        if note is not None and duration is not None:
            self.output.append(f"NOTE {note} {duration}")

    def process_chord_element(self, node):
        notes = []
        duration = None
        for child in node.children:
            if child.node_type == "ChordNotes":
                for note_child in child.children:
                    if note_child.node_type == "Note":
                        notes.append(self.note_to_midi(note_child.value))
            elif child.node_type == "Duration":
                duration = float(child.value)
        if notes and duration is not None:
            notes_str = " ".join(map(str, notes))
            self.output.append(f"CHORD {notes_str} {duration}")

    def process_tempo(self, node):
        self.tempo = int(node.value)
        self.output.append(f"TEMPO {self.tempo}")

    def process_command(self, node):
        if node.value.lower() in ["play", "share", "save"]:
            self.output.append(node.value.upper())
        else:
            print(f"Warning: Unknown command '{node.value}'")

    def note_to_midi(self, note):
        note_map = {
            "C": 0, "C#": 1, "D": 2, "D#": 3, "E": 4, "F": 5, "F#": 6,
            "G": 7, "G#": 8, "A": 9, "A#": 10, "B": 11
        }
        base_note = note[:-1]  # Extract the note name (C, D#, etc.)
        octave = int(note[-1])  # Extract the octave as an integer
        return 12 * (octave + 1) + note_map[base_note]