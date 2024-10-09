class SentenceProcessing:
    def __init__(self, max_words_before_phone_number_or_email =20):
        self.MIN_LENGTH_PHONE = 8
        self.max_words_before_phone_number_or_email = max_words_before_phone_number_or_email
        
    def contains_letters(self, word):
        return any(char.isalpha() for char in word)
    
    def contains_numbers(self, word):
        return any(char.isdigit() for char in word)
        
    def count_numbers(self, word):
        i=0
        word = word.split(' ')
        word = ''.join(word)
        for char in word:
            if char.isdigit():
                i += 1
        return i
        
    def is_phone(self, word):
        return self.contains_numbers(word) and self.count_numbers(word) > self.MIN_LENGTH_PHONE
        
    def is_email(self,word):
        return self.contains_letters(word) and '@' in word and '.' in word
        
    def get_text_elements(self, text):
        max_words_before_phone_number_or_email = self.max_words_before_phone_number_or_email 
        splited_text = [ n.strip() for n in text.split('\n') if (n.strip() != '')]  # split all text by '\n' to text elements
        number_of_words_before_phone_or_email = 0
        p_text_liste = []
        for index, elem in enumerate(splited_text):
            if (self.is_phone(elem) or ('@' in elem and '.' in elem)): # if elem contains phone number or email
                if(number_of_words_before_phone_or_email==0):
                    p_text_liste.append(elem)
                else:
                    last_elems_tokens = (" ".join([elem_ for elem_ in splited_text[index-number_of_words_before_phone_or_email:index]])).split()
                    last_min = min(max_words_before_phone_number_or_email, len(last_elems_tokens))
                    p_text_liste.append(" ".join(last_elems_tokens[-last_min:]))
                    p_text_liste.append(elem)
                number_of_words_before_phone_or_email = 0
            else:
                number_of_words_before_phone_or_email += 1
        return p_text_liste

    def word_process(self, word):
        new_word = ""
        if (self.contains_letters(word) or (not self.contains_numbers(word))) and ('@' not in word):
            if word[0].isdigit():
                last_type = "digit"
            elif word[0].isalpha():
                last_type = "alpha"
            else:
                last_type = "other"
                
            for i, char in enumerate(word):
                if (char.isdigit() and last_type == "digit") or (char.isalpha() and last_type == "alpha"): # the same type
                    new_word += char
                elif char.isdigit() and last_type != "digit":
                    new_word += " " + char
                    last_type = "digit"
                elif char.isalpha() and last_type != "alpha":
                    new_word += " " + char
                    last_type = "alpha"
                    
                else : # char is other
                    if last_type == "alpha" and (char not in ["+","-","("]):
                        new_word += char
                        last_type = "other"
                        
                    elif last_type == "digit" :
                        new_word += char
                        last_type = "other"
                        
                    elif last_type == "other" and (len(new_word)>0 and (new_word[-1] not in [":",",","،",".","?","!"]) or (char in [":",",","،",".","?","!"])):
                        new_word += char
                    else:
                        new_word += " " + char
                        last_type = "other"
        else:
            new_word = word
        return new_word.strip()
        
    def sentence_process(self, text_elements) :
        new_text_elements = []
        for sentence in text_elements:
            words = sentence.split(' ')
            new_words = []
            for word in words:
                if word != '':
                    new_word = self.word_process(word)
                    if new_word != '':
                        for wrd in new_word.split(' '):
                            new_words.append(wrd)
                        
            new_sentence = ""
            for index, word in enumerate(new_words):
                if not self.contains_letters(word):  # word = number or [+ ( ) - . , ...]
                    if len(new_sentence) > 0 :
                        if self.contains_letters(new_sentence.split(' ')[-1]) : # or (not self.contains_numbers(new_sentence.split(' ')[-1])) or (not self.contains_numbers(word))
                            new_sentence += " "+word
                        # if two numbers
                        elif self.contains_numbers(new_sentence.split(' ')[-1]) and self.count_numbers(new_sentence.split(' ')[-1]) > self.MIN_LENGTH_PHONE and self.count_numbers(word) > self.MIN_LENGTH_PHONE :
                            new_sentence += " "+word
                        # if number with number or with [+ ( ) - . , ...]
                        else:
                            new_sentence += word
                    else:
                        new_sentence += word
                else :
                    if len(new_sentence) > 0 :
                        new_sentence += " "+word
                    else :
                        new_sentence += word
            
            new_text_elements.append(new_sentence.strip())
        return new_text_elements
        
    def clean_phone(self,text_elements):
        new_text_elements = []
        for sentence in text_elements:
            sentence_list = sentence.split(' ')
            new_sentence_list = []
            for word in sentence_list:
                new_phone_number = word
                if self.is_phone(word): # word == phone number
                    start_index = -1;
                    end_index = -1
                    len_phone = len(word)
                    for i, char in enumerate(word):
                        if ( char.isdigit() or char in ["+","(","-"] ) and start_index == -1:
                            start_index = i
                            
                        if ( word[len_phone-1 - i].isdigit() or word[len_phone-1 - i] == ")" ) and end_index == -1:
                            end_index = len_phone - i
                            
                        if start_index != -1 and end_index != -1:
                            break
                            
                    new_phone_number= word[start_index:end_index]
                    if start_index != 0:
                        new_phone_number = word[0:start_index] + " " + new_phone_number
                    if end_index != len_phone :
                        new_phone_number += " " + word[end_index:len_phone]
                        
                new_sentence_list.append(new_phone_number)
                
            new_text_elements.append((" ".join(new_sentence_list)).strip())
        return new_text_elements
    
    def reduce_words_before_phone_and_email(self, liste_elements):
        max_words_bitween_phones_emails = self.max_words_before_phone_number_or_email
        new_liste_elements = []
        number_of_words_before_phone_or_email = 0
        for elem in liste_elements:
            liste_words_at_elem = elem.split()
            new_liste_words_at_elem = []
            for index, word in enumerate(liste_words_at_elem):
                if self.is_phone(word) or self.is_email(word) : # word in elem is a phone or an email
                    if (number_of_words_before_phone_or_email <= index) : # add juste words in the same elem
                        min_number_before = min(number_of_words_before_phone_or_email, max_words_bitween_phones_emails)
                        for wrd in liste_words_at_elem[index-min_number_before: index+1]:
                            new_liste_words_at_elem.append(wrd)
                    else:  # add words in the same elem and in the previous elem ( if the previous elem does not contain phone or email )
                        if index >= max_words_bitween_phones_emails:
                            for wrd in liste_words_at_elem[index-max_words_bitween_phones_emails: index+1]:
                                new_liste_words_at_elem.append(wrd)
                            if not (self.is_phone(new_liste_elements[-1]) or self.is_email(new_liste_elements[-1])):
                                new_liste_elements.pop()
                        else:
                            for wrd in liste_words_at_elem[0: index+1]:
                                new_liste_words_at_elem.append(wrd)
                                
                    number_of_words_before_phone_or_email = 0
                else:                                           # word in elem is not a phone and not an email
                    number_of_words_before_phone_or_email += 1
                    
            if not new_liste_words_at_elem:
                if new_liste_elements :
                    if not any([ self.is_phone(wrd) or self.is_email(wrd) for wrd in new_liste_elements[-1].split()]) :
                        new_liste_elements.pop()
                new_liste_elements.append(elem)
            else:
                new_liste_elements.append(" ".join(new_liste_words_at_elem))
        return new_liste_elements
        
    def extract_chunks(self, p_text_liste, max_len_chunk = 200, pad = 6):
        new_text = ' |&| '.join(p_text_liste)
        text_list = new_text.split()
        len_text_list = len(text_list)
        n_chunks= int(len_text_list / max_len_chunk) + 1
        chunks = []
        for i in range(n_chunks):
            if i == 0:
                start = i*max_len_chunk
                end = min((i+1)*max_len_chunk,len_text_list)
            else:
                start = end - pad
                end = min(((i+1)*max_len_chunk) - pad , len_text_list)
                
            chunk = text_list[start:end]
            chunks.append(' '.join(chunk))
            
            if i == n_chunks-1 and end != len_text_list and len(chunk)==max_len_chunk:
                start = end - pad
                end = len_text_list
                chunk = text_list[start:end]
                chunks.append(' '.join(chunk))
        return chunks

    def get_chunks_from_clean_html_text(self, clean_html):
        text_elements = self.get_text_elements(clean_html)
        text_elements = self.sentence_process(text_elements)
        text_elements = self.clean_phone(text_elements)
        text_elements = self.reduce_words_before_phone_and_email(text_elements, max_words_bitween_phones_emails=10)
        chunks = self.extract_chunks(text_elements)
        return chunks

    def get_new_clean_text(self, clean_html_text):
        text_elements = self.get_text_elements(clean_html_text)
        return '\n'.join(text_elements)