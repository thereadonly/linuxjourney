from typing import List
from bs4 import BeautifulSoup
from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse,RedirectResponse

app = FastAPI()
app.mount("/static", StaticFiles(directory="../lessons"), name="static")
templates = Jinja2Templates(directory="../templates")

def parse_lesson(f: Path) -> str:
    return f.stem[3:].lower()

def parse_category(f: Path) -> str:
    return f.stem[3:].lower()

def parse_lessons_order(f: Path) -> List[str]:
    return [parse_lesson(Path(l)) for l in f.read_text().splitlines()]


all_lessons = list(Path("../lessons/locales/en_english").glob("**/*.html"))
lessons_mapper = {
        f"{parse_category(f.parent)}/{parse_lesson(f)}":f for f in all_lessons
    }
page_to_category = {
    parse_lesson(f):parse_category(f.parent) for f in all_lessons
}

category_to_pages = {parse_category(f.parent):parse_lessons_order(f) for f in Path("../lessons/locales/en_english").glob("**/*.txt")}

@app.get("/",response_class=HTMLResponse)
async def root():
    return open("../lessons/locales/en_english/index.html",'r',encoding="utf-8").read()



@app.get("/lesson/{category}/{id}", response_class=HTMLResponse)
async def read_item(request: Request,category:str, id: str):
    lesson = f"{category}/{id}"
    bs = BeautifulSoup(open(lessons_mapper[lesson],'r',encoding="UTF-8"))
    page = str(bs.find("div",{"class":"markdown-body"}))
    exe_i = page.index("<h3>Exercise</h3>")
    try:
        quiz_i = page.index("<h3>Quiz Question</h3>")
    except ValueError:
        try:
            quiz_i = page.index("<h3>Quiz Questions</h3>")
        except ValueError:
            quiz_i = len(page) - 1 
    content = page[len('<div class="markdown-body">'):exe_i]
    exe = page[exe_i:quiz_i]
    quiz = page[quiz_i:]
    menu = category_to_pages[category]
    return templates.TemplateResponse("lesson.html", {
        "request": request,
         "page": id,
         "category":category,
          "content": content,
          "exercise":exe,
          "quiz":quiz,
          "menu":menu})


@app.get("/lesson/{id}", response_class=RedirectResponse)
async def read_item(request: Request, id: str):
    return RedirectResponse(f"/lesson/{page_to_category[id]}/{id}")