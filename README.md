# MusicLang Lexical Grammar

## Overview
MusicLang is a programming language designed for composing music through code. This document outlines the lexical grammar defining the token types used in MusicLang.

## Token Types

### 1. Note
- **Description**: Represents individual musical notes, which can be specified with their pitch and octave.
- **Examples**: 
    - C4 (Middle C)
    - D#5 (D sharp in the fifth octave)
    - E3 (E in the third octave)
- **Pattern**: A-G(#[0-9]+|b[0-9]*)?[0-9]

### 2. Chord
- **Description**: Represents multiple notes played together simultaneously.
- **Examples**: 
    - chord C4 D4 (C and D played together)
    - chord A3 C5 E5 (A, C, and E played simultaneously)
- **Pattern**: chord (A-G(#[0-9]+|b[0-9]*)?[0-9]+)(?: (A-G(#[0-9]+|b[0-9]*)?[0-9]+))+

### 3. Duration
- **Description**: Represents the length of time a note or chord is played, often specified in beats or fractions of a beat.
- **Examples**: 
    - 1.0 (one whole beat)
    - 0.5 (half a beat)
    - 0.75 (three-quarters of a beat)
- **Pattern**: (1|0\.[0-9]+|0?[1-9])

### 4. Tempo
- **Description**: Represents the speed of the music, commonly defined in beats per minute (BPM). Tempo affects the overall pace of the composition.
- **Examples**: 
    - 1.5 (indicating the tempo for a section)
    - 120 (120 BPM)
    - 90 (90 BPM)
- **Pattern**: ([0-9]+(\.[0-9]+)?)

### 5. Play
- **Description**: Represents the action of playing a note or chord.
- **Examples**: play
- **Pattern**: play

### 6. Share
- **Description**: Represents the action of sharing a musical composition or code.
- **Examples**: share
- **Pattern**: share
