import speech_recognition as sr
import pyttsx3
from gramformer import Gramformer
gf = Gramformer(models=1)
r=sr.Recognizer()
def SpeakText(command):
    engine=pyttsx3.init()
    voice=engine.getProperty("voices")
    engine.setProperty("voice",voice[1].id)
    engine.say(command)
    engine.runAndWait()
while(True):
    try:
        with sr.Microphone() as source:
            print("Wait to Speak!")
            r.adjust_for_ambient_noise(source)
            print("Start Speaking")
            audio=r.listen(source)
            speech=r.recognize_google(audio)
            print("You said "+speech)
            SpeakText(speech)
            SpeakText("Let me check grammar!")
            checker=gf.correct(speech)
            SpeakText(checker)
    except sr.UnknownValueError:
            print("An Error Occurred")
    
