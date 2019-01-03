import HTMLParser

def escape(html):
    """Returns the given HTML with ampersands, quotes and carets encoded."""
    return html.replace('\n',' ').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;').replace("'", '&#39;')

class wechatContentParser(HTMLParser.HTMLParser):
    parseState = ""
    strContent = ""
    strPostDate = ""
    strAuthor = ""
    strAbstract = ""
    strThumbnail = ""
    strTitle = ""
    strSource = ""
    #strArticle = ""
    
    def handle_starttag(self, tag, attrs):
        if tag == "title":
            self.parseState = "Source"
        for attr in attrs:
            if attr[0] == "id":
                if attr[1] == "post-date":
                    self.parseState = "PostDate"
                    break
            if attr[0] == "class":
                if attr[1] == "rich_media_title":
                    self.parseState = "Title"
                if attr[1] == "rich_media_meta rich_media_meta_text":
                    self.parseState = "Author"
                if attr[1] == "rich_media_content":
                    self.parseState = "Content"
                    #self.strContent=""
                if attr[1] == "rich_media_thumb":
                    self.parseState = "Thumbnail"
                if attr[1] == "rich_media_meta rich_media_meta_link rich_media_meta_nickname":
                    self.parseState = "Source"
                #if attr[1] == "comment_quote":
                #    self.parseState = "comment_quote_1"
            if attr[0] == "src" and self.parseState == "Thumbnail":
                #self.strThumbnail = attr[1]
                #self.ParseState = "ignore"
                return
    def handle_endtag(self, tag):
        if tag == "title" and self.parseState == "Source":
            self.parseState = "ignore"
            strTemp = "\""+self.strContent+"\",\n"
            #self.f_output.write(strTemp)
            #print(strTemp)
        return
    def handle_data(self, data):
        if self.parseState == "PostDate":
            self.strPostDate = data;
            self.parseState = "ignore"
        if self.parseState == "Author":
            #print ("Author:", data)
            self.strAuthor = data.strip()
            self.parseState = "ignore"
        if self.parseState == "Content":
            #print ("Content:", data)
            self.strContent += escape(data)
            return
        if self.parseState == "comment_quote_2":
            self.strAbstract = data
            self.parseState = "ignore"
            return
        if self.parseState == "comment_quote_1":
            self.parseState = "comment_quote_2"
            return
        intStart = data.find("var cover =")
        if (intStart>0):
            intEnd = data.find("/0")
            self.strThumbnail = data[intStart+13:intEnd+2]
            return
        if self.parseState == "Title":
            self.strTitle = data.strip() 
            self.parseState = "ignore"
            return
        if self.parseState == "Source":
            self.strSource = data.strip() 
            self.parseState = "ignore"
            return
            
    