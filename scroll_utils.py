from rgbmatrix import graphics

class ScrollText:
    def __init__(self, text, font, color, y_pos, start_x, end_x, speed=0.2):
        self.text = text 
        self.font = font
        self.color = color
        self.y = y_pos
        self.start_x = start_x
        self.end_x = end_x
        self.speed = speed 
        self.text_width = sum([self.font.CharacterWidth(ord(char)) for char in self.text])
        self.current_x = float(start_x)

    def draw(self, canvas):
        # Use int() for the drawing position
        int_x = int(self.current_x)
        
        temp_x = int_x
        for char in self.text:
            char_width = self.font.CharacterWidth(ord(char))
            # Only draw if the character is within the horizontal bounds
            if temp_x + char_width > self.start_x and temp_x < self.end_x:
                graphics.DrawText(canvas, self.font, temp_x, self.y, self.color, char)
            temp_x += char_width

        # Increment movement and check for reset
        self.current_x -= self.speed
        if self.current_x + self.text_width < self.start_x:
            self.current_x = float(self.end_x)

    def update_text(self, new_text):
        if self.text != new_text:
            self.text = new_text
            self.text_width = sum([self.font.CharacterWidth(ord(c)) for c in self.text])
            # Start again from the beginning when text changes
            self.current_x = float(self.start_x)
