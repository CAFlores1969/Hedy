from object_3d import *
from camera import *
from projection import *

import pygame #manejo de las ventanas
from pygame.locals import *
import win32con
import win32gui
import win32api

#Speech
import threading #permite paralelismo
from multiprocessing import Value, Array, Queue
import os

import speech_recognition #voz a texto
import pyttsx3 #texto a voz
import pywhatkit #carga videos de youtube
import datetime, locale
import wikipedia
import subprocess #ejecuta programas de linea de coamdos
import re #estandariza texto para eliminar los asentos
from unicodedata import normalize
import random
from pytube import Playlist
import pyautogui #envia teclado a aplicacion, en este caso para poner youtube en modo cine
#import pyperclip # permite enviar datos al portapapeles pyperclip.copy('hola')
import time #genera espera en algunos procesos para liberar procesador

from googletrans import Translator #pip install googletrans==3.1.0a0, para el traductor
from gtts import gTTS #de texto a voz para el traductor
from playsound import playsound #pip install playsound==1.2.2 , para reproducir la voz del traductor
import winsound #para producir el beep
from requests import get #obtiene informacion de pagina web


class SoftwareRender:
    def __init__(self):
        pygame.init()
        self.RES = self.WIDTH, self.HEIGHT = 200, 240
        self.H_WIDTH, self.H_HEIGHT = self.WIDTH // 2, self.HEIGHT // 2
        self.FPS = 60
        self.screen = pygame.display.set_mode(self.RES, pygame.NOFRAME, pygame.RESIZABLE)
        pygame.display.set_caption(title)
        self.clock = pygame.time.Clock()
        #parametros iniciales
        self.colorFondo = (0,128,0)#(255, 0, 255) #'black'

        hwnd = win32gui.FindWindow(None, title) #Busca identificar la ventana
        win32gui.SetWindowLong(hwnd, win32con.GWL_EXSTYLE,
                               win32gui.GetWindowLong(hwnd, win32con.GWL_EXSTYLE) | win32con.WS_EX_LAYERED)
        # Set window transparency color
        win32gui.SetLayeredWindowAttributes(hwnd, win32api.RGB(*self.colorFondo), 0, win32con.LWA_COLORKEY)
        # Dispone ventana sobre todo
        win32gui.SetWindowPos(hwnd, win32con.HWND_TOPMOST, 0, 0, 0, 0, win32con.SWP_NOSIZE)

        #self.colorLine = 'green'
        self.posLeftRight = 0
        self.posUpDown = -4.1
        self.zoom = -18.1
        self.pathObj = 'hedy.obj'
        self.speedRot = 0.01

        self.create_objects()

    def create_objects(self):
        self.camera = Camera(self, [self.posLeftRight, self.posUpDown, self.zoom]) #[izq/der, arriba/abajo, zoom]
        self.projection = Projection(self)
        self.object = self.get_object_from_file(self.pathObj)
        self.object.rotate_y(-math.pi / 4)

    def get_object_from_file(self, filename):
        vertex, faces = [], []
        with open(filename) as f:
            for line in f:
                if line.startswith('v '):
                    vertex.append([float(i) for i in line.split()[1:]] + [1])
                elif line.startswith('f'):
                    faces_ = line.split()[1:]
                    faces.append([int(face_.split('/')[0]) - 1 for face_ in faces_])
        return Object3D(self, vertex, faces, colorLine=colorLine)

    def draw(self):
        self.screen.fill(pygame.Color(self.colorFondo)) #Color ded Fondo
        self.object.draw(speedRot=self.speedRot, colorLine=(mRed.value, mGreen.value, 0))

    def run(self):
        self.font = pygame.font.SysFont('Arial', 12)
        winMovida = False

        while h.is_alive():
            if not (minimizado.value):
                self.draw()

                text = self.font.render(entiendo.value, True, pygame.Color('green'))
                #text = self.font.render_to(self.screen, (0, 0), text='Hola Mundo.', fgcolor='green', bgcolor='black')
                self.screen.blit(text, (10, 190))

                self.camera.control()
                #pygame.display.set_caption(str(self.clock.get_fps()))
                pygame.display.flip()
                #detecta si mouse esta sobre ventana para moverla
                x, y = pyautogui.position()
                if x >=0 and x <= 200 and y >= 0 and y <= 240 :
                    if not winMovida :
                        hwnd = win32gui.FindWindow(None, title)
                        win32gui.MoveWindow(hwnd, 200, 0, 200, 240, True)
                        winMovida = True
                else:
                    if winMovida:
                        hwnd = win32gui.FindWindow(None, title)
                        win32gui.MoveWindow(hwnd, 0, 0, 200, 240, True)
                        winMovida = False


            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    detener_hedy.value = True

            self.clock.tick(self.FPS)

''' 
** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
Speech
** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** ** *
'''
def load_play_list(): # Listado de playlist favoritos PUBLICOS para poner musica
    listas = [
        'https://www.youtube.com/playlist?list=PLTwcVto04J2E4anmLGQlf-BStyP1skBaW',
        'https://www.youtube.com/playlist?list=PLTwcVto04J2GbAWod-E76qedXGq71SOFm',
        'https://www.youtube.com/playlist?list=PLTwcVto04J2Fce6C5_7iBUdqO70LOaF-O'
    ]
    for lista in listas:
        pl =  Playlist(lista)
        ##print(lista + " Video: " + str(len(pl)))
        for url in pl.videos:
            #print(url.title)
            videos.append(url.watch_url)
            titulos.append(url.title)
    return None

def talk(text):
    engine.say(text)
    engine.runAndWait()

def listenCommand():
    listener = speech_recognition.Recognizer()
    with speech_recognition.Microphone() as source:
        ##print("Escuchando...")
        #Cambia el color a verde
        mRed.value = 0
        mGreen.value = 255

        listener.pause_threshold = 1
        listener.energy_threshold = 300
        listener.adjust_for_ambient_noise(source) ###
        voice = listener.listen(source, phrase_time_limit=6)
        #Cambia el color a rojo
        mRed.value = 255
        mGreen.value = 0
    try:
        query = listener.recognize_google(voice, language="es-US")
    except Exception as e:
        ##print('no entiendo')
        return "None"
    return query

def hedy():
    hour = int(datetime.datetime.now().hour)
    if hour>=0 and hour<12:
        saludo = 'Buenos dias'
    elif hour>=12 and hour<19:
        saludo = 'Buenas tardes'
    else:
        saludo = 'Buenas noches'
    talk(saludo)

    while not(detener_hedy.value):
        rec = listenCommand()
        rec = rec.lower()
        entiendo.value = rec.encode("utf-8")
        ##print('Lo que entiendo: ' + rec)

        if yourName in rec:
            winsound.Beep(2000, 100)
            rec = rec.replace(yourName, '')
            cmdOriginal = rec #Se usa para el traductor

            # -> NFD y eliminar diacríticos
            rec = re.sub(r"([^n\u0300-\u036f]|n(?!\u0303(?![\u0300-\u036f])))[\u0300-\u036f]+", r"\1", normalize( "NFD", rec), 0, re.I)
            # -> NFC
            rec = normalize( 'NFC', rec)

            #Comandos
            if 'reproduce' in rec:
                music = rec.replace('reproduce', '')
                ##print('music: ' + music)
                pywhatkit.playonyt(music)
                talk('reproduciendo ' + music)
            if 'mi ip' in rec:
                ip = get('https://api.ipify.org/').text
                talk('tu ip publica es ' + ip)
            elif 'traduce' in rec: #validar cuando el texto es vacio
                rec = cmdOriginal.replace('traduce','').strip()
                translator = Translator() #Translator(service_urls=['translate.googleapis.com'])
                ##print('traduciendo: ' + rec)
                text_to_translate = translator.translate(rec, src = "es", dest="en",)
                text = text_to_translate.text
                try:
                    os.remove("voice.mp3")
                    speakgl = gTTS(text=text, lang="en", slow=True)
                    speakgl.save("voice.mp3")
                    talk(rec + " en ingles se dice")
                    playsound("voice.mp3")
                except:
                    talk("Lo siento, no puedo traducir este texto.")
            elif 'repite' in rec:
                #Repite la ultima traduccion
                playsound("voice.mp3")
            elif 'pon musica' in rec:
                talk('estoy preparando la musica')
                ##print("cantidad de videos: " + str(len(videos)))
                indice = random.randint(0,len(videos)-1)

                #"C:\Program Files\VideoLAN\VLC\vlc.exe" :network-caching=1000M https://www.youtube.com/watch?v=8C6xDjQ66wM
                comando = "start chrome.exe /incognito --disable-accelerated-video --disable-gpu --disable-plugins --disable-extensions --disable-translate --app=\"data:text/html,<html><body><script>window.moveTo(580,240);window.resizeTo(800,600);window.location='-AquiVideo-';</script></body></html>\""
                comando = comando.replace('-AquiVideo-',videos[indice])

                subprocess.call(comando, shell=True)
                time.sleep(3)

                talk('reproduciendo ' + titulos[indice])
                pyautogui.press("t")
            elif 'estas ahi' in rec:
                minimizado.value = False
                hwnd = win32gui.FindWindow(None, title)  # Busca identificar la ventana
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                talk('aqui estoy')
            elif 'minimiza' in rec:
                talk('Minimizando')
                hwnd = win32gui.FindWindow(None, title)  # Busca identificar la ventana
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
                minimizado.value = True
            elif 'abre' in rec:
                sites={
                    'google':'google.com',
                    'youtube':'youtube.com',
                    'whatsap':'whatsapp.com'
                }
                for i in list(sites.keys()):
                    if i in rec:
                        talk(f'abriendo {i}')
                        subprocess.call(f'start chrome.exe {sites[i]}', shell=True)
            elif 'hora es' in rec:
                hora = datetime.datetime.now().strftime('%I:%M %p')
                talk('son las ' + hora)
            elif 'es hoy' in rec:
                fecha = datetime.datetime.now().strftime("%A %d %B %Y")
                ##print(fecha)
                talk('hoy es ' + fecha)
            elif 'que es' in rec:
                order = rec.replace('que es', '')
                wikipedia.set_lang("es")
                info = wikipedia.summary(order, 1)
                ##print('wiki: ' + info)
                talk(info)
            elif 'apagate' in rec:
                talk('hasta la vista beibi')
                detener_hedy.value = True
            else:
                talk('disculpa, no entiendo lo que dices')

    talk('terminé')

if __name__ == '__main__':
    minimizado = Value('i', False)
    title = 'Hedy Lamarr'
    colorLine = 'red'

    if True:
        '''
        *** Speech
        '''
        videos = []
        titulos = []
        v = threading.Thread(target=load_play_list)
        v.start()

        yourName = 'siri' # Nombre al cual responde
        locale.setlocale(locale.LC_ALL, "es-ES")

        engine = pyttsx3.init()
        rate = engine.getProperty('rate')
        engine.setProperty('rate', 170)  # rate-30)
        volume = engine.getProperty('volume')
        engine.setProperty('volume', volume + 1)
        voices = engine.getProperty('voices')
        engine.setProperty('voice', voices[2].id)

        # Color para las lineas del objeto entre procesos
        mRed = Value('d', 255)
        mGreen = Value('d', 0)
        entiendo = Array('c', 255)
        entiendo.value = b'Hola Perrin.'

        detener_hedy = Value('i', False)
        h = threading.Thread(target=hedy)
        h.start()

    app = SoftwareRender()
    app.run()
    #pip freeze
    #pyinstaller --windowed --onefile --icon=./hedy.ico hedy4.py