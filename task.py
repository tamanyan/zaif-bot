
import urllib
from time import sleep

for i in range(0, 10000):
    print("rquest {}: http://localhost:8080/save_btc".format(i))
    result = urllib.urlopen("http://localhost:8080/save_btc").read()
    sleep(60 * 3)