from fastapi import FastAPI
app = FastAPI()
ind = {
    'delhi': ['Red Fort', 'Qutub Minar', 'India Gate'],
    'mumbai': ['Gateway of India', 'Marine Drive', 'Elephanta Caves'],
    'jaipur': ['Hawa Mahal', 'Amber Fort', 'City Palace']
}
@app.get("/get/{name}")
async def hello(name):
    return f"My name is {ind.get(name)}"



