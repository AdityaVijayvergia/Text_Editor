from objects import Page, Line
from queue import Queue

class TextEditor:
    def __init__(self, start_text = '', make_pages = True):
        self.PAGE_SIZE = 20
        self.LINE_SIZE = 1000
        # Change lINE_SIZE to a lower value to see pages and lines
        # self.LINE_SIZE = 10
        self.MAX_PAGE_SIZE = self.PAGE_SIZE*2
        self.MAX_LINE_SIZE = self.LINE_SIZE*2
        self.init_editor(start_text, make_pages)

        self.dictionary = set()
        # On windows, the dictionary can often be found at:
        # C:/Users/{username}/AppData/Roaming/Microsoft/Spelling/en-US/default.dic
        # with open("/usr/share/dict/words") as input_dictionary:
        with open("C:/Users/adity/AppData/Roaming/Microsoft/Spelling/en-US/default.dic") as input_dictionary:
            for line in input_dictionary:
                words = line.strip().split(" ")
                for word in words:
                    self.dictionary.add(word)
        self.dictionary = sorted(self.dictionary)
        self.dic_cache = {}
        self.cache_len = 0
        self.max_cache_len = 100
        self.dic_queue = Queue()
        self.paste_text = ""


    def init_editor(self, text, make_pages = True):
        multiplier = 1
        self.line_head = Line(text[:self.LINE_SIZE])
        self.page_head = Page(first_line = self.line_head, last_char_pos=self.line_head.text_length, total_lines=1)
        self.all_pages = [(1, self.page_head)]

        text_len = len(text)

        if text_len<self.LINE_SIZE:
            return

        l = self.line_head
        if make_pages:
            p = self.page_head
            self.total_pages = 1
        
        while (multiplier+1)*self.LINE_SIZE < text_len:

            l.next = Line(text[multiplier*self.LINE_SIZE:(multiplier+1)*self.LINE_SIZE])
            l = l.next
            multiplier+=1
            
            if make_pages:
                if p.total_lines >= self.PAGE_SIZE:
                    p.next_page = Page(first_line = l, total_lines=1)
                    p.next_page.last_char_pos = p.last_char_pos + l.text_length
                    
                    p=p.next_page
                    self.total_pages += 1
                    self.all_pages.append((self.total_pages, p))

                else:
                    p.total_lines += 1
                    p.last_char_pos += l.text_length
            
        if text[multiplier*self.LINE_SIZE:]!='':
            l.next = Line(text[multiplier*self.LINE_SIZE:])
            if make_pages:
                p.last_char_pos += l.next.text_length
                p.total_lines+=1


    def print_all_lines(self):
        p = self.line_head
        while p:
            print(p.text, end = '-->')
            p = p.next


    def print_all_page(self):
        p = self.page_head
        l = p.first_line
        print('\n\n___________________new page____________________')

        while l:
            if p.next_page and l == p.next_page.first_line:
                p = p.next_page
                print('\n___________________new page____________________')
            print(l.text, end = '-->')
            # print(l.text, l.next, l.text_length, end = '\n')
            l = l.next
        # print('\nend of text~~~~~~~~~~~~~')

    def get_page_for_pos(self, pos):
        l = 0
        r = len(self.all_pages) - 1

        while l<r:
            m = (l+r)//2

            if self.all_pages[m][1].last_char_pos >= pos and self.all_pages[m-1][1].last_char_pos < pos:
                l = m
                break

            if self.all_pages[m][1].last_char_pos < pos:
                l = m + 1
            
            else:
                r = m
        
        return self.all_pages[l][1], l

    def get_text(self, start=0, end=None):
        if end == None:
            end = self.all_pages[-1][1].last_char_pos
        start_page, start_pos = self.get_page_for_pos(start)
        end_page, end_pos = self.get_page_for_pos(end)

        pre_chars = 0

        if start_pos > 0:
            pre_chars = self.all_pages[start_pos-1][1].last_char_pos
            start -= pre_chars

        if start_page == end_page:
            end -= pre_chars
            return start_page.get_text(start, end)

        text = start_page.get_text(start, start_page.last_char_pos)

        page_idx = start_pos + 1
        while page_idx!= end_pos:
            text += self.all_pages[page_idx][1].get_text(0, self.all_pages[page_idx][1].last_char_pos - self.all_pages[page_idx-1][1].last_char_pos)
            page_idx += 1

        text+=end_page.get_text(0, end - self.all_pages[end_pos-1][1].last_char_pos)

        return text


    def paste(self, pos):
        target_page, page_idx = self.get_page_for_pos(pos)

        if page_idx > 0:
            pos -= self.all_pages[page_idx-1][1].last_char_pos

        # pos is the start pos for target page
        line = target_page.first_line
        char_seen = self.all_pages[page_idx-1][1].last_char_pos + line.text_length
        lines_seen = 1

        while line.next and pos - line.text_length>=0:
            line = line.next
            lines_seen += 1
            char_seen += line.text_length
            pos = pos - line.text_length
        
        target_line = line
        target_line_pos = pos

        # case: only added to target line
        if target_line.text_length + len(self.paste_text) <= self.MAX_LINE_SIZE:
            target_line.text = target_line.text[:target_line_pos] + self.paste_text + target_line.text[target_line_pos:]
            target_line.text_length = len(target_line.text)
            target_page.last_char_pos += len(self.paste_text)
            # self.print_all_page()
            return
        
        # case: new lines needed
        else:
            # replace text following the insert position in target line
            t = target_line.text[target_line_pos:]
            self.paste_text += t
            target_line.text = target_line.text[:target_line_pos] + self.paste_text[:len(t)]
            self.paste_text = self.paste_text[len(t):]
                
        after_target_line = target_line.next
        after_target_page = target_page.next_page
        
        # now add self.paste_text in new lines after target line
        paste_line_head = Line(self.paste_text[:self.LINE_SIZE])
        target_line.next = paste_line_head
        char_seen+=self.LINE_SIZE
        # target
        lines_seen+=1
        text_len = len(self.paste_text)

        l = paste_line_head
        target_page.total_lines = lines_seen
        target_page.last_char_pos = char_seen
        multiplier = 1

        while (multiplier+1)*self.LINE_SIZE < text_len:
            
            l.next = Line(self.paste_text[multiplier*self.LINE_SIZE:(multiplier+1)*self.LINE_SIZE])
            l = l.next

            if target_page.total_lines > self.PAGE_SIZE:
                # add new page
                if page_idx >= len(self.all_pages):
                    self.all_pages.append((page_idx, target_page))
                else:
                    self.all_pages[page_idx] = (page_idx, target_page)
                page_idx += 1
                target_page.next_page = Page(first_line = l, last_char_pos=target_page.last_char_pos)
                target_page = target_page.next_page
                
            
            target_page.total_lines+=1
            target_page.last_char_pos += l.text_length
            multiplier+=1

            
        if self.paste_text[multiplier*self.LINE_SIZE:]!='':
            if after_target_line and after_target_line.text_length + len(self.paste_text[multiplier*self.LINE_SIZE:]) <= self.MAX_LINE_SIZE:
                after_target_line.text = self.paste_text[multiplier*self.LINE_SIZE:] + after_target_line.text
                after_target_line.text_length = len(after_target_line.text)
            else:
                l.next = Line(self.paste_text[multiplier*self.LINE_SIZE:])
                l=l.next
                target_page.total_lines+=1
                target_page.last_char_pos+=l.text_length
        
        l.next = after_target_line
        while l.next and (after_target_page==None or l.next != after_target_page.first_line):
            l = l.next
            target_page.last_char_pos+=l.text_length
            target_page.total_lines+=1
        
        
        target_page.next = after_target_page
        if page_idx >= len(self.all_pages):
            self.all_pages.append((page_idx, target_page))
        else:
            self.all_pages[page_idx] = (page_idx, target_page)
        page_idx += 1
        target_page = target_page.next

        while target_page:
            if page_idx >= len(self.all_pages):
                self.all_pages.append((page_idx, target_page))
            else:
                self.all_pages[page_idx] = (page_idx, target_page)
            page_idx += 1
            target_page.last_char_pos+=len(self.paste_text)

            target_page = target_page.next_page


    def copy(self, i, j):
        self.paste_text = self.get_text(i,j)



    def cut_from_same_line(self, start_page, start_line, pre_line, start, end):
        self.paste_text = start_line.text[start:end]
        start_line.text = start_line.text[:start] + start_line.text[end:]
        start_line.text_length -= end - start


        # combine with line
        if start_line.text_length < self.LINE_SIZE:
            
            if start_line.next and (start_page.next_page == None or (start_page.next_page and start_page.next_page.first_line != start_line.next)):
                start_line.text += start_line.next.text
                # start_page.last_char_pos += start_line.next.text_length
                start_line.text_length += start_line.next.text_length
                # start_page.next_page.total_lines -= 1
                start_line.next = start_line.next.next

            elif pre_line and start_line!=start_page.first_line:
                # print('used')
                # combine with prev line
                pre_line.text += start_line.text
                pre_line.text_length += start_line.text_length
                pre_line.next = start_line.next
                start_line = pre_line
            
            start_page.total_lines -= 1
                
        start_page.last_char_pos -= end - start

        p = start_page.next_page

        while p:
            p.last_char_pos -= end - start
            p = p.next_page

        return

    def cut(self, start, end):

        if end<=start:
            self.paste_text = ''
            return

        start_page, start_page_idx = self.get_page_for_pos(start)
        start_page_copy = start_page
        start_copy = start
        line = start_page.first_line
        lines_seen = 0
        chars_to_cut = end - start

        if start_page_idx>0:
            start = start - self.all_pages[start_page_idx-1][1].last_char_pos
            end = end - self.all_pages[start_page_idx-1][1].last_char_pos

        
        # start and end are start and end when taking 0 at start_page

        pre_line = None
        while line.next and start - line.next.text_length >= 0:
            pre_line = line
            if start_page.next_page and line.next == start_page.next_page.first_line:
                start_page = start_page.next_page 
            line = line.next
            lines_seen += 1
            start = start - line.text_length
            end = end - line.text_length
        if start_page.next_page and line == start_page.next_page.first_line:
            start_page = start_page.next_page 
        start_line = line
        lines_seen += 1
        start_page.total_lines = lines_seen


        # if in end and start in same line
        if end <= start_line.text_length:
            return self.cut_from_same_line(start_page, start_line, pre_line, start, end)
            

        # if start and end in different lines
        self.paste_text = start_line.text[start:]
        
        lines_to_cut = 0
        end_page = start_page
        end -= start_line.text_length

        line = start_line

        while line.next and end - line.next.text_length>=0:
            if end_page.next_page and end_page.next_page.first_line == line.next:
                end_page = end_page.next_page
                lines_to_cut = 0
            line = line.next
            self.paste_text += line.text
            lines_to_cut += 1
            end = end - line.text_length

        if end_page.next_page and end_page.next_page.first_line == line.next:
            end_page = end_page.next_page
            lines_to_cut = 0
        
        end_page.total_lines -= lines_to_cut
        end_line = line.next
        # end, end_line, end_page all set


        self.paste_text += end_line.text[:end]

        # if start and end lines can be combined
        if start_line.text_length - end + start <= self.MAX_LINE_SIZE:
            start_line.text_length = end_line.text_length - end + start
            start_line.text = start_line.text[:start] + end_line.text[end:]

            end_page.first_line = start_line
            start_page.last_char_pos -= start
            start_page.total_lines -= 1
            start_line.next = end_line.next
            end_line = start_line.next
        
        else:
            start_line.text = start_line.text[:start]
            start_line.text_length = start
            end_line.text = end_line.text[end:]
            end_line.text_length -= end
            start_line.next = end_line
            end_page.first_line = end_line


        # now only step left is combining pages
        # if no change in page required after merging
        if self.MAX_PAGE_SIZE >= start_page.total_lines + end_page.total_lines:
            # merge start and end page
            start_page.total_lines += end_page.total_lines
            start_page.last_char_pos = end_page.last_char_pos - chars_to_cut
            start_page.next_page = end_page.next_page

        else:
            start_page.next_page = end_page
            start_page.last_char_pos = start_copy
            end_page.last_char_pos -= chars_to_cut
            start_page = end_page

        # remain:  modify last_char_pos for following pages 
        self.modify_following_pages_after_cut(start_page, chars_to_cut, start_page_copy, start_page_idx)


    def modify_following_pages_after_cut(self, modify_start_page, chars_to_cut, start_page, start_page_idx):
        p = modify_start_page.next_page

        while p:
            p.last_char_pos -= chars_to_cut
            p = p.next_page

        while start_page:
            self.all_pages[start_page_idx] = (start_page_idx, start_page)
            start_page_idx += 1
            start_page = start_page.next_page
        
        self.all_pages = self.all_pages[:start_page_idx]


    def dictionary_search(self, word):
        # binary search
        l = 0
        r = len(self.dictionary)

        while l<=r:
            m = (l+r)//2
            if self.dictionary[m] == word:
                return True
            elif self.dictionary[m]>word:
                r = m - 1
            else:
                l = m + 1
        
        return False



    def misspellings(self):
        result = 0
        line = self.line_head
        while line:
            words = line.text.split(" ")
            line = line.next
            for word in words:
                if word in self.dic_cache:
                    if self.dic_cache[word] == False:
                        result = result + 1
                else:       

                    if not self.dictionary_search(word):
                        result = result + 1
                        self.dic_cache[word] = False
                    else:
                        self.dic_cache[word] = True
                    self.cache_len += 1
                    if self.cache_len > self.max_cache_len:
                        self.dic_cache.pop(self.dic_queue.get())
                        self.dic_queue.put(word)
                        self.cache_len -= 1

        return result




        

def main():
    ttxt = '0123456789abcdefghij0123456789abcdefghij'
    editor = TextEditor(ttxt)
    editor.print_all_page()

    editor.paste_text = 'abcdef'
    editor.paste(5)
    editor.print_all_page()

    editor.copy(5,10)
    editor.paste(13)
    editor.print_all_page()

    editor.cut(2,5)
    editor.print_all_page()
    print('\n\npaste_text = ',editor.paste_text)
    editor.cut(5,12)
    editor.print_all_page()
    print('\n\npaste_text = ',editor.paste_text)

if __name__=='__main__':
    main()