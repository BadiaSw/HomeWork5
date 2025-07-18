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
        self.wheels = wheels
        self.reflector_map = reflector_map

    def encrypt_letter(self, ch):
        if not ('a' <= ch <= 'z'):
            return ch

        w1, w2, w3 = self.wheels
        offset = ((2 * w1) - w2 + w3) % ALPHABET_SIZE

        index = self.hash_map[ch]
        index += offset if offset != 0 else 1
        index %= ALPHABET_SIZE

        char1 = next((key for key, val in self.hash_map.items() if val == index), "")

        reflected = self.reflector_map[char1]
        index = self.hash_map[reflected]

        index -= offset if offset != 0 else 1
        index %= ALPHABET_SIZE

        final_char = next((key for key, val in self.hash_map.items() if val == index), "")
        return final_char

    def step(self, count):
        # Advance W1
        self.wheels[0] = self.wheels[0] + 1 if self.wheels[0] < W1_MAX else W1_MIN

        # Advance W2
        self.wheels[1] = self.wheels[1] * 2 if count % 2 == 0 else self.wheels[1] - 1

        # Advance W3 based on encryption count
        if count % 10 == 0:
            self.wheels[2] = 10
        elif count % 3 == 0:
            self.wheels[2] = 5
        else:
            self.wheels[2] = 0

    def set_wheels(self, wheels):
        self.wheels = list(wheels)

    def encrypt(self, message):
        result = []
        original_wheels = self.wheels.copy()
        encrypted_count = 0

        for ch in message:
            encrypted_ch = self.encrypt_letter(ch)
            result.append(encrypted_ch)

            # Count only real encryptions of lowercase letters
            if 'a' <= ch <= 'z':
                encrypted_count += 1
                self.step(encrypted_count)

        self.set_wheels(original_wheels)
        return ''.join(result)
    
def valid(wheels, hash_map, reflector_map):
    if wheels is None or hash_map is None or reflector_map is None:
        raise JSONFileException("Invalid JSON file: missing keys")

    if not (W1_MIN <= wheels[0] <= W1_MAX):
        raise JSONFileException("Invalid wheel1: out of range")

    if wheels[2] not in W3_VALUES:
        raise JSONFileException("Invalid wheel3: must be 0, 5, or 10")

    if len(hash_map) != 26 or set(hash_map.values()) != set(range(FIRST_LETTER_INDEX, LAST_LETTER_INDEX + 1)):
        raise JSONFileException("Invalid hash map: must map all 26 letters to unique values from 0 to 25")

    for char, val in hash_map.items():
        if not ('a' <= char <= 'z') or not (FIRST_LETTER_INDEX <= val <= LAST_LETTER_INDEX):
            raise JSONFileException(f"Invalid hash map entry: {char}:{val}")

    for a, b in reflector_map.items():
        if not ('a' <= a <= 'z') or not ('a' <= b <= 'z'):
            raise JSONFileException(f"Invalid reflector map entry: {a}->{b} is not lowercase")
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

        valid(wheels, hash_map, reflector_map)
        return Enigma(hash_map, wheels, reflector_map)

    except (json.JSONDecodeError, KeyError, TypeError) as e:
        raise JSONFileException("Error reading from file.") from e
    
def main():
    args = sys.argv[1:]
    config_file = input_file = output_file = None

    try:
        # Manual flag parsing to allow any order
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
                f.write('\n'.join(encrypted_lines))
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