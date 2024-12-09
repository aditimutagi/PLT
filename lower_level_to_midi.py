from mido import MidiFile, MidiTrack, Message, MetaMessage
import zipfile
import pygame
import os


class MIDI_LowerLevel:
    def __init__(self):
        self.midi_file = MidiFile()
        self.track = MidiTrack()
        self.midi_file.tracks.append(self.track)
        self.output_dir = "output"
        os.makedirs(self.output_dir, exist_ok=True)

    def bpm_to_microseconds(self, bpm):
        return int(60000000 / bpm)

    def add_tempo(self, bpm):
        self.tempo = bpm
        self.track.append(MetaMessage('set_tempo', tempo=self.bpm_to_microseconds(self.tempo)))

    def add_note(self, midi_note, duration):
        # Convert beats to ticks (assuming 480 ticks per beat)
        ticks = int(duration * 480)
        self.track.append(Message('note_on', note=midi_note, velocity=64, time=0))
        self.track.append(Message('note_off', note=midi_note, velocity=64, time=ticks))

    def add_chord(self, midi_notes, duration):
        ticks = int(duration * 480)
        # Start all notes simultaneously
        for note in midi_notes:
            self.track.append(Message('note_on', note=note, velocity=64, time=0))
        # End all notes simultaneously
        for note in midi_notes:
            self.track.append(Message('note_off', note=note, velocity=64, time=ticks if note == midi_notes[-1] else 0))

    def parse_and_generate(self, instructions):
        """
        Parses instructions and generates MIDI tracks. Instructions are grouped into
        sequences that are processed after encountering a TEMPO line.
        """
        lines = instructions.strip().split("\n")
        current_sequence = []  # Buffer for instructions
        current_tempo = None  # No tempo set initially

        for line in lines:
            tokens = line.split()
            action = tokens[0]

            if action == "TEMPO":
                # If we encounter a tempo, process the previous sequence with the current tempo
                current_tempo = int(tokens[1])
                if current_sequence:
                    if current_tempo is None:
                        raise ValueError("A TEMPO must be set before notes or chords.")
                    self.add_tempo(current_tempo)
                    self.process_sequence(current_sequence)
                    current_sequence = []  # Reset the sequence buffer
                
            else:
                # Add instruction to the current sequence
                current_sequence.append(line)


    def process_sequence(self, sequence):
        """
        Processes a sequence of instructions at the specified tempo.
        """
        for line in sequence:
            tokens = line.split()
            action = tokens[0]

            if action == "NOTE":
                midi_note = int(tokens[1])
                duration = float(tokens[2])
                self.add_note(midi_note, duration)
            elif action == "CHORD":
                midi_notes = list(map(int, tokens[1:-1]))
                duration = float(tokens[-1])
                self.add_chord(midi_notes, duration)


    def save_midi_file(self, filename="output.mid"):
        midi_file_path = os.path.join(self.output_dir, filename)
        self.midi_file.save(midi_file_path)
        print(f"\nMIDI file saved to {midi_file_path}")
        return midi_file_path


    def play_midi_file(self, midi_file_path):
        # Initialize pygame mixer
        pygame.mixer.init()
        pygame.mixer.music.load(midi_file_path)
        pygame.mixer.music.play()

        # Keep the script running while the MIDI file is playing
        print("\nPlaying MIDI file")
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)  # Wait until the music finishes

    def zip_midi_file(self, midi_file_path, shareable_file = "shareable_midi_files.zip"):
        shareable_file_path = os.path.join(self.output_dir, shareable_file)
        with zipfile.ZipFile(shareable_file_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            zipf.write(midi_file_path, os.path.basename(midi_file_path))
        print(f"File {midi_file_path} zipped as {shareable_file_path}. You can share it via email.")




    def handle_command(self, instructions):
        self.parse_and_generate(instructions)

        filename = self.save_midi_file()
        
        if "PLAY" in instructions:
            self.play_midi_file(filename)

        if "SHARE" in instructions:
            self.zip_midi_file(filename)

