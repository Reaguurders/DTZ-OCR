from PIL import Image, ImageEnhance
from io import BytesIO
from pytesseract import image_to_string
from selenium import webdriver
from threading import Thread
import time


# Je wilt waarschijnlijk OCR ook als aparte Thread, maar had het al opgegeven voordat ik hieraan begon
# Zou er ongeveer zo uitzien:
# class OCR(Thread):
#    def run(self):
#        print("OCR: ")
#        print(image_to_string(Image.open(PATH_NAAR_SCREENSHOT), lang="nld"))
from selenium.webdriver.support.wait import WebDriverWait


class Screen(Thread):
    count = 0

    def run(self):
        # Selenium met chromedriver naar De Dumpert Topzoveel
        global driver
        driver = webdriver.Chrome('chromedriver')
        driver.get('https://www.dumpert.nl/mediabase/7590061/1a3188c7/de_dumpert_topzoveel.html')

        # Kudtkookiewet
        if "kudtkoekiewet.nl" in driver.current_url:
            # Beter om dit ook via jQuery via de website te doen.
            driver.find_element_by_css_selector('.approve-btn').click()

        # Setup, anders probeer nog een keer (erg nasty manier om dit te doen)
        while not self.setup():
            time.sleep(0.25)
        self.loop()

    def setup(self):
        # Via jQuery op de website (sneller en geen crash als die t element als nog niet kan vinden).
        # Niet bijzonder belangrijk verder, geluid uit + de overlay weg.
        if len(driver.find_elements_by_class_name('vjs-mute-control')) > 0:
            driver.execute_script("$('.vjs-mute-control').click()")
            driver.execute_script('$("kqa3").addClass("vjs-user-inactive").removeClass("vjs-user-active")')
            time.sleep(3)
            return True
        else:
            return False

    def loop(self):
        print("loop")
        self.count += 1

        # Hier moet je eigenlijk wachten totdat de video HD geladen is, anders zijn de screenshots sowieso hopeloos.

        # element is de vide player
        element = driver.find_element_by_id('kqa3EqTHEOplayerBqa')
        location = element.location
        size = element.size

        # Dit kan zoveel netter.
        img = driver.get_screenshot_as_png()
        # driver.get_screenshot_as_base64()
        im = Image.open(BytesIO(img))
        # im = ImageEnhance.Contrast(im).enhance(15)

        left = location['x']
        bottom = location['y'] + size['height']
        top = bottom - 75
        right = left + 500
        im = im.crop((left, top, right, bottom))

        # Opslaan naar images folder
        im.save('images/screenshot' + str(self.count) + '.png')

        # Dit wil je dus eigenlijk threaden in OCR want nu kan die niet iedere seconde een screenshot maken
        # als die te lang over de OCR doet.
        # Side note: lang="nld" is traag en werkt eigenlijk niet goed, maar haalt sommige woorden er wel beter uit dan default (lang='eng')
        print(image_to_string(Image.open(self), lang="nld"))

        # Sleep voor 1 seconde en restart de loop
        time.sleep(1)
        self.loop()


# Start de Thread
Screen().start()
