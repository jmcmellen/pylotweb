import requests
from bs4 import BeautifulSoup
import re

payload = {"formatType":"DOMESTIC",
           "retrieveLocId":"3dw\nbbg\neos",
           "reportType":"REPORT",
           "actionType":"notamRetrievalByICAOs"}

r = requests.post("https://pilotweb.nas.faa.gov/PilotWeb/notamRetrievalByICAOAction.do?method=displayByICAOs",
                  data=payload)

soup = BeautifulSoup(r.text)
qtyNotamsParser= re.compile('.*Number of NOTAMs:\D*(\d+)')
asrNotamsParser= re.compile('.*ASR.(\d+)\).TIL.(\d+).*')
#print soup.prettify()

for qtyNotams in soup.findAll(id="alertFont"):
    #print unicode(qtyNotams.get_text())
    m = qtyNotamsParser.match(unicode(qtyNotams.get_text()))
    if m is not None:
        numNotams = int(m.group(1))
        print "Number of Notams is", numNotams


for notam in soup.findAll(id="notamRight"):
    notamText = notam.get_text()
    print notamText
    j = asrNotamsParser.search(notamText)
    #print j
    #print asrNotamsParser.findall(notamText)
    if j is not None:
        asr = int(j.group(1))
        expireTime = int(j.group(2))
        #print j.group(0)
        print "ASR number", asr
        print "Expires", expireTime
