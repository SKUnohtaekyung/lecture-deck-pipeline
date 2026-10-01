import sys, json, urllib.parse
sys.stdout.reconfigure(encoding='utf-8')
BASE = 'http://localhost:8799/'
DECK = BASE + urllib.parse.quote('tmp/frame/E1/t/강의덱.html')
