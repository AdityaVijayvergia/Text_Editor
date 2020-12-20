class Page:
    def __init__(self,first_line = None, total_lines = 0,last_char_pos = 0, next_page = None):
        self.total_lines = total_lines
        self.first_line = first_line
        self.last_char_pos = last_char_pos
        self.next_page = next_page

    def get_line_for_pos(self, pos, line=None):
        if not line:
            line = self.first_line

        while line and pos - line.text_length>=0:
            line = line.next
            if not line:
                return line, -1
            pos = pos - line.text_length
        
        return line, pos


    def get_text(self, start, end):

        start_line, start_pos = self.get_line_for_pos(start) 

        if not start_line:
            return ''

        if end <= start - start_pos + start_line.text_length:
            end_pos = end - start + start_pos
            return start_line.text[start_pos:end_pos]

        text = start_line.text[start_pos:]
        p = start_line.next

        while p and end >= start + len(text) + p.text_length:
            if self.next_page and self.next_page.first_line == p:
                return text
            text += p.text
            p = p.next
        
        if p and end > start + len(text):
            text += p.text[:end - start - len(text)]

        return text



class Line:
    def __init__(self, text='', next_line=None):
        self.next = next_line
        self.text = text
        self.text_length = len(text)
