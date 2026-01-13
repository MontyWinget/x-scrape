import time
from collect.twitter_selenium import get_driver

driver = get_driver()
driver.get("https://twitter.com/home")
time.sleep(30)
driver.quit()
