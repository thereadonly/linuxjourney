from pathlib import Path
from markdownserver.markdown_converter import MarkdownConverter

converter = MarkdownConverter()
for p in Path(r"../lessons/locales/en_english/").glob("**/*.md"):
    new_path = p.with_suffix(".html")
    converter.convert(str(p),str(new_path))

    utf_meta = """<meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />"""    
    
    data = open(new_path,'r',encoding="UTF-8").read()
    i = data.index("</head>")
    data = data[:i] + utf_meta + data[i:]
    data = data.replace("""<h2>Lesson Content</h2>""","").replace("h2","h3").replace("h1","h3")

    open(new_path,'w',encoding="UTF-8").write(data)
