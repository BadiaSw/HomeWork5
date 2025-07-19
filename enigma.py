import json
import sys

# Constants
FIRST_LETTER_INDEX = 0
LAST_LETTER_INDEX = 25
ALPHABET_SIZE = LAST_LETTER_INDEX - FIRST_LETTER_INDEX + 1
W1_MIN = 1
W1_MAX = 8
W3_VALUES = (0, 5, 10)

class JSONFileException(Exception):
    pass

class Enigma:
    def __init__(self, hash_map, wheels, reflector_map):
        self.hash_map = hash_map
        self.wheels = list(wheels)
        self.reflector_map = reflector_map

    def encrypt_letter(self, ch):
     if not ('a' <= ch <= 'z'):
        return ch

     w1, w2, w3 = self.wheels
     offset = ((2 * w1) - w2 + w3) % ALPHABET_SIZE
     if offset == 0:
        offset = 1

    # Forward shift using offset
     i = self.hash_map[ch]
     i = (i + offset) % ALPHABET_SIZE
     c1 = next((key for key, value in self.hash_map.items() if value == i), "")

    # Reflection
     c2 = self.reflector_map[c1]
     i = self.hash_map[c2]

    # Reverse shift using offset
     i = (i - offset) % ALPHABET_SIZE
     return next((key for key, value in self.hash_map.items() if value == i), "")

 

    def step(self, count):
        self.wheels[0] = self.wheels[0] + 1 if self.wheels[0] < W1_MAX else W1_MIN
        self.wheels[1] = self.wheels[1] * 2 if count % 2 == 0 else self.wheels[1] - 1

        if count % 10 == 0:
            self.wheels[2] = 10
        elif count % 3 == 0:
            self.wheels[2] = 5
        else:
            self.wheels[2] = 0

    def set_wheels(self, wheels):
        self.wheels = list(wheels)

    def encrypt(self, message):
        result = ""
        original_wheels = self.wheels.copy()
        num_of_encryptions = 0

        for ch in message:
            encrypted = self.encrypt_letter(ch)
            result += encrypted

            if 'a' <= ch <= 'z' and ch != encrypted:

                num_of_encryptions += 1
                self.step(num_of_encryptions)

        self.set_wheels(original_wheels)
        return result

    def encrypt_using_file(self, input_path):
        try:
            with open(input_path, 'r') as file:
                return [self.encrypt(line.rstrip('\n')) for line in file]
        except Exception:
            print("The enigma script has encountered an error", file=sys.stderr)
            sys.exit(1)

def is_valid(wheels, hash_map, reflector_map):
    if wheels is None or hash_map is None or reflector_map is None:
        raise JSONFileException("Invalid JSON file")

    if not (W1_MIN <= wheels[0] <= W1_MAX):
        raise JSONFileException("Invalid wheel1")
    if wheels[2] not in W3_VALUES:
        raise JSONFileException("Invalid wheel3")

    if len(hash_map) != 26 or set(hash_map.values()) != set(range(FIRST_LETTER_INDEX, LAST_LETTER_INDEX + 1)):
        raise JSONFileException("Invalid hash map")

    for c, n in hash_map.items():
        if not ('a' <= c <= 'z') or not (FIRST_LETTER_INDEX <= n <= LAST_LETTER_INDEX):
            raise JSONFileException(f"Invalid hash map entry: {c}:{n}")

    for a, b in reflector_map.items():
        if not ('a' <= a <= 'z') or not ('a' <= b <= 'z'):
            raise JSONFileException(f"Invalid reflector map entry: {a}->{b}")
        if a == b:
            raise JSONFileException(f"Invalid reflector map: {a} maps to itself")
        if reflector_map.get(b) != a:
            raise JSONFileException(f"Invalid reflector symmetry: {a}->{b} but {b}->{reflector_map.get(b)}")

def load_enigma_from_path(path):
    try:
        with open(path, 'r') as f:
            data = json.load(f)

        wheels = data.get("wheels")
        hash_map = data.get("hash_map")
        reflector_map = data.get("reflector_map")

        is_valid(wheels, hash_map, reflector_map)
        return Enigma(hash_map, wheels, reflector_map)

    except (json.JSONDecodeError, KeyError, TypeError):
        raise JSONFileException("Error reading from file.")

def main():
    args = sys.argv[1:]
    config_file = input_file = output_file = None

    try:
        i = 0
        while i < len(args):
            if args[i] == '-c':
                i += 1
                config_file = args[i]
            elif args[i] == '-i':
                i += 1
                input_file = args[i]
            elif args[i] == '-o':
                i += 1
                output_file = args[i]
            else:
                raise ValueError("Unknown flag")
            i += 1

        if not config_file or not input_file:
            raise ValueError("Missing required flags")

        enigma = load_enigma_from_path(config_file)
        encrypted_lines = enigma.encrypt_using_file(input_file)

        if output_file:
            with open(output_file, 'w') as f:
                f.write('\n'.join(encrypted_lines) + '\n')
        else:
            print('\n'.join(encrypted_lines))

    except (ValueError, IndexError):
        print("Usage: python3 enigma.py -c <config_file> -i <input_file> -o <output_file>", file=sys.stderr)
        sys.exit(1)
    except Exception:
        print("The enigma script has encountered an error", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
