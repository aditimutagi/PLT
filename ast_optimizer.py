from ast_parser import ASTNode

class ASTOptimizer:
    def __init__(self, ast):
        self.ast = ast

    def optimize(self):
        self.optimize_node(self.ast)

    def optimize_node(self, node):
        if node.node_type in {"S", "Composition", "Sequence", "Element", "Command"}:
            optimized_children = []
            for child in node.children:
                optimized_child = self.optimize_node(child)
                if optimized_child is not None:  
                    optimized_children.append(optimized_child)
            node.children = optimized_children

        elif node.node_type == "NoteElement":
            if self.has_zero_duration(node):
                return None  

        elif node.node_type == "ChordElement":
            if self.has_zero_duration(node):
                return None  

            return self.simplify_chord_with_single_note(node)

        return node

    def simplify_chord_with_single_note(self, chord_node):
        notes = []
        duration = None

        for child in chord_node.children:
            if child.node_type == "ChordNotes":
                notes = child.children
            elif child.node_type == "Duration":
                duration = child.value

        if len(notes) == 1:  
            note_element = ASTNode(node_type="NoteElement")
            note = ASTNode(node_type="Note", value=notes[0].value)
            note_element.add_child(note)
            duration_node = ASTNode(node_type="Duration", value=duration)
            note_element.add_child(duration_node)
            return note_element

        return chord_node  

    def has_zero_duration(self, node):
        for child in node.children:
            if child.node_type == "Duration" and float(child.value) == 0:
                return True
        return False