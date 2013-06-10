import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt

def main():
    locations = ['3dw', 'bbg', 'eos']
    towers = ['1007705', '1007704', '1005399']
    print "Searching locations {locations} for towers {towers}".format(
        locations=locations, towers=towers)

    payload = {"formatType":"DOMESTIC",
               "retrieveLocId":"\n".join(locations),
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
            asr = j.group(1)
            expireTime = j.group(2)
            #print j.group(0)
            print "ASR number", asr
            print "Expires", expireTime, decodeTime(expireTime)

def decodeTime(timestamp):
    return dt.strptime(timestamp, "%y%m%d%H%M")

if __name__ == "__main__":
    main()
