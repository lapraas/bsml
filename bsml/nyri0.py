import imageio

def load_font():
    alphabet = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ,'"
    font_img = imageio.imread("assets/fonts/jones.png")
    img_dim = font_img.shape[:2]

    # Separate letters
    letter_offsets = []
    letter_widths = []
    start = 0
    for i in range(1, img_dim[1]):
        if font_img[0, i, 2] > 100:
            if i > start:
                letter_offsets.append(start)
                letter_widths.append(i - start)
            start = i + 1
    assert len(letter_offsets) == len(alphabet)

    # Convert the letters to walls (1 pixel = 1 unit)
    font = {}
    for k in range(len(alphabet)):
        letter = alphabet[k]
        letter_img = font_img[
            :, letter_offsets[k]:letter_offsets[k] + letter_widths[k], :3]
        letter_matrix = ( # boolean 2-dim list for each pixel having color
            (letter_img[:, :, 0]
                + letter_img[:, :, 1]
                + letter_img[:, :, 2]) > 100)
        letter_walls = []  # list of x, y, w, h
        while True:
            h_lines = [] # list of lengths of all horizontal lines?
            v_lines = [] # same ^ but for vertical?
            # Horizontal lines
            for i in range(img_dim[0]):
                start_j = None # checker to make sure we're not adding new pixels when we can just append to a horizontal line
                for j in range(letter_widths[k]):
                    if letter_matrix[i, j] and start_j is None:
                        start_j = j
                    if not letter_matrix[i, j] and start_j is not None:
                        h_lines.append((j - start_j, i, start_j))
                        start_j = None
                if start_j is not None:
                    h_lines.append(
                        (letter_widths[k] - start_j, i, start_j))
            # Vertical lines
            for j in range(letter_widths[k]):
                start_i = None
                for i in range(img_dim[0]):
                    if letter_matrix[i, j] and start_i is None:
                        start_i = i
                    if not letter_matrix[i, j] and start_i is not None:
                        v_lines.append((i - start_i, start_i, j))
                        start_i = None
                if start_i is not None:
                    v_lines.append(
                        (img_dim[0] - start_i, start_i, j))
            # Choose the longest line, add it and clear the pixels
            h_lines.sort(key=lambda x: x[0], reverse=True)
            v_lines.sort(key=lambda x: x[0], reverse=True)
            if not h_lines and not v_lines:
                break
            elif not h_lines or v_lines[0][0] >= h_lines[0][0]:
                h, i, j = v_lines[0]
                letter_walls.append((j, img_dim[0] - i - h, 1, h))
                for r in range(i, i + h):
                    letter_matrix[r, j] = False
            else:
                w, i, j = h_lines[0]
                letter_walls.append((j, img_dim[0] - i - 1, w, 1))
                for c in range(j, j + w):
                    letter_matrix[i, c] = False
        font[letter] = (letter_widths[k], letter_walls)

    font[" "] = (5, [])

    return font

def getTextWidth(text, font):
    totalTextWidth = 0
    for char in text:
        if not char in font:
            raise Exception("Character '%s' is not a part of the supported alphabet" % char)
        charWidth = font[char][0]
        totalTextWidth += charWidth
    return totalTextWidth
