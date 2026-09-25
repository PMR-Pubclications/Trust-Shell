import base64
import urllib.parse

# Use the same seed configuration if applicable
RANDOM_SEED = 42

def get_random_shifts(length, count=20):
    import random
    random.seed(RANDOM_SEED)
    return [random.randint(1, max(1, length - 1)) for _ in range(count)]

def xor_cipher(data_str, key_char='X'):
    return ''.join(chr(ord(c) ^ ord(key_char)) for c in data_str)

def unshift_string(data_str, shift):
    if not data_str:
        return data_str
    shift = shift % len(data_str)
    return data_str[-shift:] + data_str[:-shift]

def descramble_api_key(scrambled_str, original_length):
    current = scrambled_str
    # Generate the exact same shift sequence in reverse
    shifts = get_random_shifts(original_length, 20)
    
    # Loop backwards from layer 20 down to 1
    for i in range(20, 0, -1):
        layer_type = i % 5
        
        if layer_type == 1:
            # Reverse of Layer Type A: Unshift + Base64 Decode
            current = unshift_string(current, shifts[i-1])
            current = base64.b64decode(current.encode('utf-8')).decode('utf-8')
        elif layer_type == 2:
            # Reverse of Layer Type B: Character Reverse + URL Unquote
            current = current[::-1]
            current = urllib.parse.unquote(current)
        elif layer_type == 3:
            # Reverse of Layer Type C: Hex Decode + XOR Masking
            current = bytes.fromhex(current).decode('utf-8')
            current = xor_cipher(current, key_char=chr(65 + (i % 26)))
        elif layer_type == 4:
            # Reverse of Layer Type D: Character Reverse + Base64 Decode
            current = current[::-1]
            current = base64.b64decode(current.encode('utf-8')).decode('utf-8')
        else:
            # Reverse of Layer Type E: URL Unquote + Unshift
            current = urllib.parse.unquote(current)
            current = unshift_string(current, shifts[i-1])
            
    return current

# --- How to use it in your target code ---
if __name__ == "__main__":
    # 1. Paste your final 20-layer scrambled string here instead of the plain key
    SCRAMBLED_STORED_KEY = "PASTE_YOUR_20_LAYER_STRING_HERE"
    
    # 2. Provide the original approximate length of your key so shifts match
    ORIGINAL_KEY_LENGTH = 31 
    
    # 3. Decode it dynamically right before making your API call
    # api_key = descramble_api_key(SCRAMBLED_STORED_KEY, ORIGINAL_KEY_LENGTH)
