from fastapi import FastAPI


app=FastAPI(title='Personal Blog')

@app.get("/")
def home():
    return {"message":"Primer blog TEST"}