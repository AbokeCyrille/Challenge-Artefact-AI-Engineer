class TableExtractor:
    def __init__(self, x_tolerance=15):
        self.x_tolerance = x_tolerance

    def extract(self, page):
        words = page.extract_words()
        if not words: return []
        
        lines_dict = {}
        for w in words:
            y = round(float(w['top']), 0)
            lines_dict.setdefault(y, []).append(w)
            
        rows = []
        for y in sorted(lines_dict.keys()):
            line_words = sorted(lines_dict[y], key=lambda x: x['x0'])
            if not line_words: continue
            
            new_row = []
            curr_text = line_words[0]['text']
            for i in range(1, len(line_words)):
                gap = line_words[i]['x0'] - line_words[i-1]['x1']
                if gap < self.x_tolerance:
                    curr_text += " " + line_words[i]['text']
                else:
                    new_row.append(curr_text)
                    curr_text = line_words[i]['text']
            new_row.append(curr_text)
            rows.append(new_row)
        return rows