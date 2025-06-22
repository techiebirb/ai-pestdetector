from google import genai
from tkinter import *
from tkinter import filedialog, messagebox, Toplevel, Label, Button
import pyttsx3
import cv2
from PIL import Image, ImageTk

engine = pyttsx3.init()
apikey = ""
client = genai.Client(api_key=apikey)

def upload_photo():
    file_path = filedialog.askopenfilename(
        title="Select an Image",
        filetypes=[("Image Files", "*.png;*.jpg;*.jpeg")]
    )
    if file_path:
        img = Image.open(file_path)
        img.save("pest.png")
        analyze_image()

def take_picture():
    messagebox.showinfo("CV2 VideoCapture Loading...", "Hold 's' to capture and 'q' to cancel.")
    video = cv2.VideoCapture(0)
    analyze = False
    while True:
        check,frame = video.read()
        if check:
            cv2.imshow("Pest Image Capture",frame)
            if cv2.waitKey(1) & 0xFF == ord("q"):
                video.release()
                cv2.destroyAllWindows()
                break
            if cv2.waitKey(1) & 0xFF == ord("s"):
                cv2.imwrite("pest.png",frame)
                video.release()
                cv2.destroyAllWindows()
                analyze = True
                break
    if analyze:
        analyze_image()
                

def analyze_image():
    try:
        pest = client.files.upload(file="pest.png")
        response = client.models.generate_content(
            model="gemini-2.0-flash",
            contents=[
                pest,
                """I have 4 things for you to do. Keep this in the perspective of a pest detection system for farmers or planters. Not if it annoys people or not.
                First, analyze the image and determine if it contains a HARMFUL pest. Again, keep this in the perspective of a pest detection system for farmers or planters. Not if it annoys people or not. If the thing detected is usually helpful but can be harmful in case of EXTREME conditions of it or amounts of it, say yes. Tend to say yes more if it on average good. Say your answer to this part in one word with a period and newline character at the end. Say "Yes" if it is a HARMFUL pest, "No" if it is just something regular, and "Unknown" if you cannot detect anything, which is unlikely, but possible.
                Second, say what kind of pest it is, just a few words, and then a period and newline character at the end. If your answer to the first part is "Unknown", then just say "N/A" and a period and newline character at the end.
                Third, provide a detailed explanation of your analysis. Keep it concise, but detailed enough to understand your reasoning. Include any relevant information about the pest, its potential harm, and any other observations you made. NO NEW NEWLINE CHARACTER AFTER EACH SENTENCE, JUST A SINGLE NEWLINE CHARACTER AT THE END OF THE ANALYSIS.
                Fourth, say what one should do about this pest, if it is harmful. If it is not harmful, say "No action needed." If you are unsure, say "Unsure about what to do." Keep it concise, but detailed enough to understand. Include any relevant information about the pest and how to deal with it.  NO NEW NEWLINE CHARACTERS AT ALL HERE.
                Don't write anything in between the detailed analysis and the determination. Just write the detailed analysis after the determination, no headers.
                Don't put any formatting in the response, just plain text."""],
        )
        largetext = response.text
        ynu = largetext.split("\n")[0].replace(".", "")
        type = largetext.split("\n")[1].replace(".", "")
        analysis = largetext.split("\n")[2]
        action = largetext.split("\n")[3]
        print(response.text)

        results = Toplevel(root)
        results.title("Analysis Result")
        results.geometry("600x1000")

        pestimg = Image.open("pest.png")
        pestimg.thumbnail((600, 600), Image.LANCZOS)
        pestimg = ImageTk.PhotoImage(pestimg)
        pestimglabel = Label(results, image=pestimg)
        pestimglabel.image = pestimg
        pestimglabel.pack(pady=10)

        if ynu == "Yes":
            Label(results, text="Harmful Pest Detected!", font=("Arial", 32, "bold"), fg="red3").pack(pady=10)
            engine.say("Harmful Pest Detected!")
        elif ynu == "No":
            Label(results, text="No Harmful Pest Detected!", font=("Arial", 32, "bold"), fg="green4").pack(pady=10)
            engine.say("No Harmful Pest Detected!")
        else:
            Label(results, text="Unsure about Harmful Pest.", font=("Arial", 32, "bold"), fg="orange red").pack(pady=10)
            engine.say("Unsure about Harmful Pest.")
        
        pesttypeframe = Frame(results)
        pesttypeframe.pack(pady=10)
        Label(pesttypeframe, text="Pest Type:", font=("Arial", 16, "bold")).pack(side=LEFT)
        Label(pesttypeframe, text=type.title(), font=("Arial", 14)).pack(side=LEFT)

        Label(results, text="Detailed Analysis:", font=("Arial", 16, "bold")).pack(pady=10)
        Label(results, text=analysis, wraplength=550, justify=LEFT, font=("Arial", 12), anchor="w").pack(pady=5, padx=10)

        Label(results, text="Action to Take:", font=("Arial", 16, "bold")).pack(pady=10)
        Label(results, text=action, wraplength=550, justify=LEFT, font=("Arial", 12), anchor="w").pack(pady=5,padx=10)

        engine.runAndWait()
    except Exception as e:
        messagebox.showerror("Error", f"An error occurred: {e}")

root = Tk()
root.title("Harmful Pest Detector")
root.geometry("500x300")


Label(root, text="Harmful Pest Detector", font=("Arial", 28, "bold")).pack(pady=30)
Label(root, text="Detect pests by uploading a photo or taking a picture.", font=("Arial", 14)).pack(pady=10)

btnframe = Frame(root)
btnframe.pack(pady=20)
Button(btnframe, text="Upload Photo", command=upload_photo, width=15, height=2).grid(row=0, column=0, padx=10)
Button(btnframe, text="Take Picture", command=take_picture, width=15, height=2).grid(row=0, column=1, padx=10)

root.mainloop()
