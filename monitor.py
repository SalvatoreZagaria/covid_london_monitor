import sys
import time
import threading

from selenium import webdriver


options = webdriver.ChromeOptions()
options.add_argument("window-size=1600x900")
options.add_argument("headless")
browser = webdriver.Chrome(options=options)

WEBSITE = "https://www.arcgis.com/apps/opsdashboard/index.html#/f94c3c90da5b4e9f9a0b19484dd4bb14"


def wait():
    time.sleep(15)


def get_nav_element():
    browser.get(WEBSITE)

    wait_thread = threading.Thread(target=wait)
    wait_thread.start()

    nav = None
    while not nav and wait_thread.is_alive():
        try:
            nav = browser.find_element_by_xpath("/html[1]/body[1]/div[1]/div[1]/div[1]/div[1]/div[1]/div[1]/margin-container[1]/full-container[1]/div[13]/margin-container[1]/full-container[1]/div[1]/div[1]/nav[1]")
        except:
            time.sleep(0.5)
            continue

    return nav


def explore_nav(nav):
    res = {}
    nav_text = None
    while not nav_text:
        nav_text = nav.text

    elements = nav_text.split("\n")

    for el in elements:
        separated = el.split(": ")
        zone = separated[0]
        number = separated[1]
        res[zone] = int(number)

    return res


def pretty_print(res):
    msg = ""
    ordered_dict = sorted(res.items(), key=lambda x: x[1], reverse=True)
    for zone, number in ordered_dict:
        if zone == "Greenwich":
            msg += "**{}: {}**\n".format(zone, number)
            continue
        msg += "{}: {}\n".format(zone, number)

    return msg


if __name__ == "__main__":
    nav = get_nav_element()
    if nav is None:
        print("Resource not found on web page.")
        sys.exit(-1)
    res = explore_nav(nav)
    msg = pretty_print(res)
    print(msg)
