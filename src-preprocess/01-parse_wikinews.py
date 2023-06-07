import xml.sax
import html
import re
import os
import json
import logging
import unidecode

outFolder = "data/wiki-20210601"
outFile = "data/wiki-20210601.json"
outCatFile = "data/wiki-20210601.categories.tsv"
inCatFile = "data/wiki-20210601.categories.ok.tsv"
wikinewsFile = "data/itwikinews-20210601-pages-articles.xml"
idPrefix = "wiki-"

logging.basicConfig(level=logging.INFO)

skipTitles = ["Notizie precedenti", "Fonti"]
toRemove = ["__TOC__", ".jpg", "|}", "}}", "]]", "__NOEDITSECTION__", "__NOTOC__", "__NOINDEX__"]

class PageHandler( xml.sax.ContentHandler ):
    def __init__(self):
        self.page = ""
        self.title = ""
        self.id = ""
        self.inPage = False
        self.inTitle = False
        self.inText = False
        self.inId = False
        self.inRevision = False
    def startElement(self, tag, attributes):
        if tag == "page":
            self.inPage = True
        if tag == "revision":
            self.inRevision = True
        if tag == "title" and self.inPage:
            self.inTitle = True
            self.title = ""
        if tag == "id":
            self.inId = True
        if tag == "text" and self.inPage:
            self.inText = True
            self.page = ""
    def endElement(self, tag):
        if tag == "text":
            self.inText = False
        if tag == "title":
            self.inTitle = False
        if tag == "id":
            self.inId = False
        if tag == "revision":
            self.inRevision = False
        if tag == "page":
            self.inPage = False
            if (not self.title.startswith("MediaWiki:") and
                not self.title.startswith("Template:") and
                not self.title.startswith("Aiuto:") and
                not self.title.startswith("File:") and
                not self.title.startswith("Portale:") and
                not self.title.startswith("Modulo:") and
                not self.title.startswith("Categoria:") and
                not self.title.startswith("Discussione utente:") and
                not self.title.startswith("Wikinotizie:") and
                not self.page.startswith("#REDIRECT")):

                print(self.id + " --- " + self.title)

                rawtext = self.page
                cats = categoryRe.findall(rawtext)
                # print(rawtext)
                rawtext = re.sub("\{\|.*?\|\}", "", rawtext, flags=re.S)
                rawtext = rawtext.replace("{{aggiorna}}", "aggiorna")

                text = ""
                for line in rawtext.splitlines():
                    cont = True
                    for t in skipTitles:
                        if line.startswith("==" + t) or line.startswith("== " + t):
                            cont = False
                    if not cont:
                        break;
                    text += str(line.strip("#=*: "))
                    text += "\n"
                    if line.endswith("<br />"):
                        text += "\n"
                    if line.startswith(":"):
                        text += "\n"
                    if line.startswith("=="):
                        text += "\n"

                # catFw
                finalCats = set()
                for cat in cats:
                    cat = unidecode.unidecode(cat)
                    parts = cat.split("|")
                    catFw.write(self.id)
                    catFw.write("\t")
                    catFw.write(parts[0])
                    catFw.write("\n")
                    if parts[0] in okCategories:
                        finalCats.add(parts[0])
                    if parts[0] in catMappings:
                        for thisCat in catMappings[parts[0]]:
                            finalCats.add(thisCat)

                text = templateRe.sub("", text)
                text = linkRe.sub("\\1", text)
                text = linkImgRe.sub("", text)
                text = link2Re.sub("\\1", text)
                text = link3Re.sub("\\1", text)

                text = text.replace("'''", "")
                text = text.replace("''", "")
                text = text.strip()
                text = re.sub(r"(?<!\n)\n(?!\n)", " ", text)
                # text = text.replace("\n\n", "\n")
                text = re.sub(r'<[^>]*?>', '', text)

                text = self.title + "\n\n" + text

                fl = str(int(self.id) // 1000)
                directory = outFolder + "/" + fl + "/"
                if not os.path.exists(directory):
                    os.makedirs(directory)

                parts = text.split("\n")
                ok_text = []
                for part in parts:
                    part = part.strip()
                    doIt = True
                    for partToRemove in toRemove:
                        if partToRemove in part:
                            doIt = False
                    if doIt:
                        ok_text.append(part)

                text = "\n".join(ok_text)
                text = re.sub(r'(\n\s*)+\n+', '\n\n', text)

                text = text.strip()

                thisObj = {}
                thisObj['text'] = text
                thisObj['id'] = idPrefix + self.id
                thisObj['labels'] = list(finalCats)
                allObjs.append(thisObj)

                with open(directory + self.id + ".txt", "w") as fw:
                    fw.write(text)

                # myobj = {'text' : text, 'format': 'textpro'}
                # x = requests.post(url, data = myobj)

                # fl = str(int(self.id) // 1000)
                # directory = outFolder + "/" + fl + "/"
                # if not os.path.exists(directory):
                #     os.makedirs(directory)

                # with open(directory + self.id + ".tsv", "w") as fw:
                #     prev = ""
                #     for line in x.text.splitlines():
                #         line = line.strip()
                #         parts = line.split("\t")
                #         if len(parts) > 4:
                #             tokenText = parts[2]
                #             if tokenText == "\"":
                #                 tokenText = "\"\"\"\""
                #             fw.write(parts[0])
                #             fw.write("\t")
                #             fw.write(tokenText)
                #             fw.write("\t")
                #             thisNer = parts[5]
                #             if thisNer != "O":
                #                 if thisNer == prev:
                #                     thisNer = "I-" + thisNer
                #                 else:
                #                     thisNer = "B-" + thisNer
                #             fw.write(thisNer)
                #             prev = parts[5]
                #         else:
                #             prev = ""
                #         fw.write("\n")

                articles.append({"title": self.title, "text": self.page})
    def characters(self, content):
        if self.inId and not self.inRevision:
            self.id = content
        if self.inTitle:
            self.title += html.unescape(content.replace("\n", " "))
        if self.inText:
            self.page += content

catMappings = {}
okCategories = []

with open(inCatFile, "r") as f:
    for line in f:
        line = line.strip()
        if len(line) == 0:
            continue

        line = unidecode.unidecode(line)
        parts = line.split("\t")
        addFirst = True
        if line.startswith("#"):
            addFirst = False
            parts[0] = parts[0][1:]

        if addFirst:
            okCategories.append(parts[0])
        if len(parts) > 1:
            catMappings[parts[0]] = parts[1:]

catFw = open(outCatFile, "w")
allObjs = []

templateRe = re.compile("\{\{[^\}]*\}\}")
categoryRe = re.compile("\[\[Categoria:([^\]]*)\]\]")
linkImgRe = re.compile("\[\[(Image|Wikinotizie|Categoria|:Categoria|File|Immagine):([^\]]*)\]\]")
linkRe = re.compile("\[\[[^\]\|]*\|([^\]\|]*)\]\]")
link2Re = re.compile("\[\[([^\]]*)\]\]")
link3Re = re.compile("\[[^ ]+ ([^\]]*)\]")
articles = []

parser = xml.sax.make_parser()
parser.setFeature(xml.sax.handler.feature_namespaces, 0)

parser.setContentHandler(PageHandler())
parser.parse(wikinewsFile)

catFw.close()

jsonString = json.dumps(allObjs, indent=4)
jsonFile = open(outFile, "w")
jsonFile.write(jsonString)
jsonFile.close()

