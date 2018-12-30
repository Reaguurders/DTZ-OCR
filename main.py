from PIL import Image
from io import BytesIO
from pytesseract import image_to_string
from selenium import webdriver
from threading import Thread
import time

from selenium.common.exceptions import StaleElementReferenceException, NoSuchElementException
from selenium.webdriver.common.keys import Keys


class Google(Thread):
    to_search = []
    searched = []

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        has_searched = False
        if len(self.to_search) > 0:
            print("Search")
            has_searched = True
            for search_key in list(set(self.to_search) - set(self.searched)):
                browser = webdriver.Chrome('chromedriver')
                browser.get('https://www.google.com')
                search = browser.find_element_by_name('q')
                search.send_keys(search_key + " site:dumpert.nl")
                try:
                    search.send_keys(Keys.RETURN)
                    browser.find_element_by_xpath("//div[@id='search']//div[@id='ires']//a[1]").click()
                except (NoSuchElementException, StaleElementReferenceException):
                    browser.quit()
                    continue

                if "kudtkoekiewet.nl" in driver.current_url:
                    browser.execute_script("setCookieAndRedirect()")
                self.to_search.remove(search_key)
                browser.quit()
                self.searched += [browser.current_url]

        if not has_searched:
            time.sleep(1)
        self.run()


class OCR(Thread):
    def __init__(self, image):
        Thread.__init__(self)
        self.image = image
        global to_search
        self.start()

    def run(self):
        image_string = image_to_string(self.image, lang="Freeroad")
        print("OCR: " + image_string)
        # print(image_to_string(self.image, lang="Freeroad"))
        if len(image_string) > 0:
            Google.to_search += [image_string]


class Screen(Thread):
    count = 0

    def run(self):
        global driver
        driver = webdriver.Chrome('chromedriver')
        driver.get('https://www.dumpert.nl/mediabase/7590061/1a3188c7/de_dumpert_topzoveel.html')

        if "kudtkoekiewet.nl" in driver.current_url:
            driver.find_element_by_css_selector('.approve-btn').click()

        while not self.setup():
            time.sleep(0.25)
        self.loop()

    def setup(self):
        if len(driver.find_elements_by_class_name('vjs-mute-control')) > 0:
            driver.execute_script("$('.vjs-mute-control').click()")
            driver.execute_script('$("kqa3").addClass("vjs-user-inactive").removeClass("vjs-user-active")')
            time.sleep(3)
            return True
        else:
            return False

    def loop(self):
        self.count += 1

        element = driver.find_element_by_id('kqa3EqTHEOplayerBqa')
        location = element.location
        size = element.size

        img = driver.get_screenshot_as_png()
        im = Image.open(BytesIO(img))

        left = location['x']
        bottom = location['y'] + size['height']
        top = bottom - 75
        right = left + 500
        im = im.crop((left, top, right, bottom))

        OCR(im)
        time.sleep(1)
        self.loop()


# Start de Thread
Screen().start()
Google().start()
