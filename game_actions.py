def is_valid_move_text(text: str):
    return len(text) == 2 and text[0].lower() in 'abc' and text[1] in '123'

def convert_move_text_to_move_number(text: str):
    letter = text[0].lower()
    number = int(text[1]) - 1
    if letter == 'b':
        number += 3
    elif letter == 'c':
        number += 6
    return number