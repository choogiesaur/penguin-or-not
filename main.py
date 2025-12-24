# main.py
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastai.learner import load_learner
from fastai.vision.core import PILImage
from starlette.requests import Request
from PIL import Image as PILImageLib
import shutil

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load your FastAI Model
model = load_learner('model.pkl')

def validate_image(file: UploadFile):
    # Check the file extension
    if file.filename.split('.')[-1].lower() not in ["jpg", "jpeg", "png"]:
        return "Invalid file type: Please upload a JPG or PNG file."

    # Read the image using PIL
    image = PILImageLib.open(file.file)

    # Check the image size (you can set your own limits)
    if image.size > (4000, 4000):
        return "Image too large: Please upload an image smaller than 4000x4000 pixels."

    # Rewind the file pointer for later use
    file.file.seek(0)

    return None

@app.get("/", response_class=HTMLResponse)
@app.post("/", response_class=HTMLResponse)
async def read_root(request: Request, file: UploadFile = File(None)):
    prediction = None
    image_path = None
    error_message = None

    if file:
        error_message = validate_image(file)
        if error_message:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error_message": error_message},
            )

        # Save uploaded image
        temp_file = "static/uploads/" + file.filename
        with open(temp_file, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)

        # Make image available for rendering
        image_path = "/static/uploads/" + file.filename

        # Run prediction
        image = PILImage.create(temp_file)
        pred, pred_idx, probs = model.predict(image)
        stringy = str(pred)
        # Convert probability to percentage
        prob_value = probs[pred_idx].item() * 100
        prediction = {"label": str(pred), "probability": f"{prob_value:.1f}%"}

    return templates.TemplateResponse(
        "index.html",
        {"request": request, "image_path": image_path, "prediction": prediction},
    )

@app.post("/predict")
async def predict(file: UploadFile = File(...)):
    image = PILImage.create(await file.read())
    pred, pred_idx, probs = model.predict(image)
    # Convert probability to percentage
    prob_value = probs[pred_idx].item() * 100
    return {"prediction": str(pred), "probability": f"{prob_value:.1f}%"}
