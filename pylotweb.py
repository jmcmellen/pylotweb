import requests
from bs4 import BeautifulSoup
import re
from datetime import datetime as dt
from datetime import timedelta
import threading
import win32console


class myThread(threading.Thread):
    def __init__(self, *args, **kwargs):
        foo = kwargs.pop('pool')
        super(myThread, self).__init__(*args, **kwargs)

    def run(self):
        #print self.getName()
        super(myThread, self).run()
        print self.getName() + " finished"


def main():
    locations = ['3dw', 'bbg', 'eos']
    towers = ['1007705', '1007704', '1005399']
    asrlist = []
    thread_list = []
    thread_pool = threading.BoundedSemaphore(value=5)

    print "Searching locations {locations} for towers {towers}".format(
        locations=locations, towers=towers)

    payload = {"formatType": "DOMESTIC",
               "retrieveLocId": "\n".join(locations),
               "reportType": "REPORT",
               "actionType": "notamRetrievalByICAOs"}

    r = requests.post("https://pilotweb.nas.faa.gov/PilotWeb/notamRetrievalByICAOAction.do?method=displayByICAOs",
                      data=payload)

    soup = BeautifulSoup(r.text)
    qtyNotamsParser = re.compile('.*Number of NOTAMs:\D*(\d+)')
    #asrNotamsParser= re.compile('.*ASR.(?P<asr>\d+)\).TIL.(?P<expTime>\d+).*')
    asrNotamsParser = re.compile('.*ASR.(?P<asr>\d+)\).*OUT OF SERVICE.(?P<fromTime>\d+)-(?P<toTime>\d+).*')
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
            asr = j.group('asr')
            toTime = j.group('toTime')
            #print j.group(0)
            asrlist.append(asr)
            print '\x1b[1;37;41m', "ASR number", '\x1b[m', asr
            print "Expires", toTime, decodeTime(toTime, 5)

    for _asr in asrlist:
        new_thread = myThread(target=getTowerInfo, pool=thread_pool, args=(_asr,thread_pool))
        new_thread.start()
        thread_list.append(new_thread)

    #print threading.enumerate()
    #for t in thread_list:
    #    t.join()

    #getTowerInfo("100770")


def decodeTime(timestamp, offset):
    return dt.strptime(timestamp, "%y%m%d%H%M") - timedelta(hours=offset)

def getTowerInfo(asrnum, thread_pool):
    thread_pool.acquire()
    payload = {"fiSearchByType":"registration_num",
               "jsValidated":"true",
               "fiSearchByValue":asrnum,
               "fiExactMatchInd":"N",
               "asr_r_state":"",
               "asr_r_zipcode":"",
               #"footerSearch":"footerSearch",
               "Submit":"Submit"}
    s = requests.Session()
    s.get("http://wireless2.fcc.gov/UlsApp/AsrSearch/asrRegistrationSearch.jsp")
    requests.utils.add_dict_to_cookiejar(s.cookies, {"selectedCountys":"cleared", "selectedStates":"cleared"})
    #print s.cookies
    #ck = requests.utils.dict_from_cookiejar(s.cookies)
    #print ck
    #asrsearch_str = ";JSESSIONID_ASRSEARCH=" + ck['JSESSIONID_ASRSEARCH']
    #asrsearch_str = ""
    #print asrsearch_str
    r = s.post("http://wireless2.fcc.gov/UlsApp/AsrSearch/asrResults.jsp",
                      data=payload,
                      params={'searchType':'TRB'},
                      headers={'content-type':'application/x-www-form-urlencoded',
                               'referer':'http://wireless2.fcc.gov/UlsApp/AsrSearch/asrRegistrationSearch.jsp'})
    thread_pool.release()
    #with open("foo.txt", "wb") as fout:
    #    fout.write(r.text)

    #print r.text
    form_regex = re.compile('(<table.*summary\="Search Results Table">.*</table>).*<table border\="0" cellpadding\="3" cellspacing\="1" width\="100%" summary\="Results pages navigation">', re.U | re.S | re.MULTILINE)
    s = form_regex.search(r.text)
    #print s.group(1)
    towerSoup = BeautifulSoup(s.group(1))
    #print towerSoup.prettify()
    towerTable = towerSoup.findAll(summary="Search Results Table")[0]
    #print towerTable.text
    result_list = []
    for row in towerTable.findAll("tr"):
        for col in row.findAll("td"):
            result_list.append(col.text.strip())
    print result_list

if __name__ == "__main__":
    main()
