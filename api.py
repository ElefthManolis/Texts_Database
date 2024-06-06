import os
from fastapi import FastAPI, Request, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import Optional
from gensim.test.utils import common_texts
from gensim.models.doc2vec import Doc2Vec, TaggedDocument


from db.postgresql import TextDB
from config.config import Config
from src.vectorizer import query_embedding

app = FastAPI()
path_to_static = os.path.join(os.path.dirname(__file__), 'static')
app.mount("/static", StaticFiles(directory=path_to_static), name="static")

class SearchQuery(BaseModel):
    query: str

@app.get("/", response_class=HTMLResponse)
async def read_root():
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Newsgroups Database</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-image: url('https://example.com/background.jpg'); /* Replace with your image URL */
                background-size: cover;
                background-position: center;
            }
            h1 {
                font-size: 80px;
            }
            .container {
                text-align: center;
                background: rgba(255, 255, 255, 0.8); /* Semi-transparent background for readability */
                padding: 20px;
                border-radius: 10px;
                display: flex;
                flex-direction: column;
                align-items: center;
            }
            .row {
                display: flex;
                justify-content: center;
                align-items: center;
                margin-bottom: 10px;
            }
            input[type="text"] {
                padding: 10px;
                font-size: 16px; /* Original font size */
                margin-right: 10px;
                width: 500px; /* Increased width */
            }
            input[type="number"] {
                padding: 10px;
                font-size: 20px; /* Increased font size */
                margin-right: 10px;
                border: 2px solid #ccc;
            }
            input[type="number"].error {
                border: 2px solid red; /* Red border for error */
            }
            select {
                padding: 10px;
                font-size: 20px; /* Increased font size */
                margin-right: 10px;
                border: 2px solid #ccc;
            }
            select.error {
                border: 2px solid red; /* Red border for error */
            }
            button {
                padding: 10px;
                font-size: 32px;
            }
            #results {
                margin-top: 20px;
                font-size: 25px;
                overflow-y: auto;
                max-height: 1400px;
            }
            #results p {
                padding-left: 100px; /* Add left padding */
                padding-right: 100px; /* Add right padding */
                text-align: left;
                overflow-y: auto;
                overflow-x: auto;
            }
            .error-message {
                color: red;
                margin-top: 5px;
                font-size: 14px;
            }
        </style>
        <script type="text/javascript" src="static/show_results.js"></script>
    </head>
    <body>
        <div class="container">
            <h1>Search Bar</h1>
            <div class="row">
                <input type="text" id="query" placeholder="Enter search query">
            </div>
            <div class="row">
                <input type="number" id="number" placeholder="Enter the top k simlarly results" min="1">
                <select id="distance_measure">
                    <option selected disabled>Distance Measure</option>
                    <option value="euclidean">Euclidean</option>
                    <option value="cityblock">City Block</option>
                    <option value="minkowski">Minkowski</option>
                    <option value="cosine">Cosine</option>
                    <option value="chebyshev">Chebyshev</option>
                    <option value="canberra">Canberra</option>
                    <option value="jensenshannon">Jensen-Shannon</option>
                </select>
            </div>
            <button id="searchButton" onclick="search()">Search</button>
            <div class="error-message" id="number-error"></div>
            <div class="error-message" id="distance_measure-error"></div>
            <div id="results"></div>
        </div>
    </body>
    
    </html>
    """
    return HTMLResponse(content=html_content)

@app.get("/search")
async def search(query: str, number: int, distance_measure: Optional[str] = Query(None, title="Distance Measure")):
    config = Config()
    db = TextDB(config)


    # embed the query in order to compute the distances
    # with the other documents
    query_embed = query_embedding(query)
    documents = db.fetch_documents(query_embed, number, distance_measure)
    
    return {"documents": documents}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)