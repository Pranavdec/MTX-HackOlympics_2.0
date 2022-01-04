

from flask import Flask, render_template, request, url_for
from werkzeug.utils import secure_filename
from tensorflow.keras.models import load_model
import cv2
import numpy as np
import io
from flask import Response
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from flask import Flask
import matplotlib as plt

app = Flask(__name__)

app.config["UPLOAD_FOLDER"] = "static/"


def basketball_score_classifer(video):

    frames_list = []
    outputs = []

    # Read the Video File using the VideoCapture object.
    video_reader = cv2.VideoCapture(video)

    # Get the total number of frames in the video.
    video_frames_count = int(video_reader.get(cv2.CAP_PROP_FRAME_COUNT))

    # Calculate the the interval after which frames will be added to the list.
    no_of_small_clips = max(int(video_frames_count/60), 1)

    for clip_counter in range(no_of_small_clips):
        frames_list = []
    # Iterate through the Video Frames.
        for frame_counter in range(20):
            video_reader.set(cv2.CAP_PROP_POS_FRAMES,
                             ((frame_counter * 3) + (clip_counter * 60)))

        # Reading the frame from the video.
            success, frame = video_reader.read()

        # Check if Video frame is not successfully read then break the loop
            if not success:
                print('not sucess')
                break
            # Resize the Frame to fixed height and width.
            resized_frame = cv2.resize(frame, (420, 420))
            resized_frame = resized_frame[:210, 80:350]

        # Normalize the resized frame by dividing it with 255 so that each pixel value then lies between 0 and 1
            normalized_frame = resized_frame / 255

        # Append the normalized frame into the frames list

            frames_list.append(normalized_frame)

        features = np.asarray(frames_list)

        test1 = (np.expand_dims(features, axis=0))

        output = model.predict(test1)

        outputs.append(output)

    # Release the VideoCapture object.
    video_reader.release()

    return outputs


plt.rcParams["figure.figsize"] = [7.50, 3.50]
plt.rcParams["figure.autolayout"] = True


@app.route('/')
def upload_file():
    return render_template('index.html')


model = load_model('finalmodel.h5')


@app.route('/', methods=['GET', 'POST'])
def display_file():
    if request.method == 'POST':
        f = request.files['file']
        filename = secure_filename(f.filename)

        f.save(app.config['UPLOAD_FOLDER'] + filename)

        content = "static/"+filename

    output = basketball_score_classifer(content)

    data = analyzing(output)

    return render_template('content.html', file_path="static/abcd.png" , data=data)


def analyzing(output):
    x = []
    for i in range(len(output)):
        x.append(i*2)

    y = []
    z = []
    for i in range(len(output)):
        if(output[i][0][0] > 0.5):
            z.append(i)
        
        y.append(output[i][0][0])

        

    fig = Figure()
    axis = fig.add_subplot(1, 1, 1)

    axis.plot(x, y)
    output = io.BytesIO()
    FigureCanvas(fig).print_png(output)

    fig.savefig('static/abcd.png')

    return z


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
