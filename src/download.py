from threading import Thread, RLock
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
import json
import time
import queue
import sys


# -------------------- settings -------------------- #
# c/i: Cache mode / Input mode
# r/n: Restore / New
# p/d: using Proxy / using Direct connection

CACHE_MODE = True if len(sys.argv) == 2 and 'c' in sys.argv[1] else False
RESTORE_FROM_FAILLOG = True if len(sys.argv) == 2 and 'r' in sys.argv[1] else False
USING_PROXY = False if len(sys.argv) == 2 and 'd' in sys.argv[1] else True

HEADER_PATH = './header.json'
SAVE_PATH = 'F:/documents/output/'

INDEX_WIDTH = 4
BEGIN = 1
END = 1

WORKER_NUM = 4
REQUEST_TIMEOUT = 8
TOKEN_INTV = 120
DOWNLOAD_INTV = 0.8

PROXY = {
    'http': 'http://127.0.0.1:4780',
    'https': 'http://127.0.0.1:4780',
}

URLS = {
    'loan': 'https://archive.org/services/loans/loan',
    'resource': None
}

# -------------------- processing -------------------- #
PARAMS = None
done = 0 # a global counter for the number of files download
total = 0 # total task number
lock = RLock() # a lock for modifying `count`
cookies_jar = requests.cookies.RequestsCookieJar()

with open(HEADER_PATH, 'r') as f:
    headers = json.load(f)


def parse_cookies(cookies):
    for item in cookies.split(';'):
        k, v = item.split('=', 1)
        k = k.strip()
        v = v.strip()
        cookies_jar.set(k, v)


def parse_request_example(example):
    host, params_str = example.split('?', 1)
    params = dict()
    for item in params_str.split('&'):
        k, v = item.split('=', 1)
        params[k] = v
    id = params['id']
    file = params['file']
    f = file.rsplit('_', 1)[0]
    ext = file.rsplit('.', 1)[1]

    # set PARAMS
    global PARAMS
    PARAMS= {
        'zip': params['zip'],
        'file': f + '_%s.' + ext,
        'id': params['id'],
        'scale': 1, # resolution of images, 1 is the best level
        'rotate': 0
    }
    # set URLS
    global URLS
    URLS['resource'] = host


class TokenUpdater(Thread):
    def __init__(self):
        super(TokenUpdater, self).__init__()
        self.__stop = False
        self.__data = {
            "action": "create_token",
            "identifier": PARAMS['id']
        }
        self.sleep_count = 0
    
    def stop(self):
        self.__stop = True

    def run(self):
        while True:
            if self.sleep_count == 0:
                self.sleep_count = TOKEN_INTV
                resp = requests.post(URLS['loan'], cookies=cookies_jar, data=self.__data, proxies=PROXY if USING_PROXY else None, timeout=REQUEST_TIMEOUT)
                cookies_jar.set('loan-{}'.format(PARAMS['id']), resp.json()['token'])
            else:
                self.sleep_count -= 1
                time.sleep(1)   # check if the main thread has finished
                if self.__stop:
                    break
            

def download(page_idx):
    page_idx = str(page_idx).rjust(INDEX_WIDTH, '0')
    par = {
        'zip': PARAMS['zip'],
        'file': PARAMS['file']%page_idx,
        'id': PARAMS['id'],
        'scale': PARAMS['scale'],
        'rotate': PARAMS['rotate']
    }

    i = 0
    while i < 3: # try 3 times if fail to request
        try:
            resp = requests.get(URLS['resource'], headers=headers, cookies=cookies_jar, params=par, proxies=PROXY if USING_PROXY else None, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                break
            else:
                raise Exception('Request Error {}'.format(resp.status_code))
        except Exception as e:
            # DO NOT show errors
            # print('Failed to download page{} [Tried {} time(s)]: {}'.format(page_idx, i+1, e))
            i += 1

    if i < 3:
        with open(SAVE_PATH+'{}.jpeg'.format(page_idx), 'wb+') as f:
            f.write(resp.content)
        
        global done
        with lock:
            cnt = done
            done += 1
        print('\rDownloading: [{}{}] {}%'.format('#'*(int(cnt/total*100)), '.'*(100-int(cnt/total*100)), round(cnt/total*100, 2)), end='', flush=True)
        time.sleep(DOWNLOAD_INTV) # wait
        return True
    return False



if __name__ == '__main__':
    # interact
    if not CACHE_MODE:
        cookies = input('cookies > ')
        example = input('request example > ')
        parse_cookies(cookies)
        parse_request_example(example)
        # save
        with open('cache', 'w+') as f:
            json.dump({'cookies': cookies, 'request_example': example}, f)
    else:
        with open('cache', 'r') as f:
            config = json.load(f)
        parse_cookies(config['cookies'])
        parse_request_example(config['request_example'])

    if RESTORE_FROM_FAILLOG:
        with open('fail.log', 'r') as f:
            tasks = list(map(lambda s: int(s.strip()), f.readlines()))
    else:
        r = input('Page range [begin(default 1)-]end > ')
        if r and '-' not in r:
            END = int(r)
        elif r:
            BEGIN, END = tuple(map(int, r.split('-')))
        tasks = list(range(BEGIN, END + 1))

    total = len(tasks)

    print('\n\n' + '='*40 + '\nDownlaod Setting\n')
    print('\tusing proxy: {}'.format('yes' if USING_PROXY else 'no'))
    print('\tmulti-threading: {}'.format('yes' if WORKER_NUM > 1 else 'no'))
    if WORKER_NUM > 1:
        print('\tnumber of working thread: {}'.format(WORKER_NUM))
    print('\tdownload interval: {} s'.format(DOWNLOAD_INTV))
    print('\ttoken interval: {} s'.format(TOKEN_INTV))
    print('\tmode: {} | {}'.format('CACHE' if CACHE_MODE else 'INPUT', 'RESTORE' if RESTORE_FROM_FAILLOG else 'NEW'))
    print()
    print('\tfile id: {}'.format(PARAMS['id']))
    print('\tpage number: {}'.format(len(tasks)))
    if not RESTORE_FROM_FAILLOG:
        print('\trange: {}-{}'.format(BEGIN, END))
    print('\n')

    # update token in a seperate thread
    token_updater = TokenUpdater()
    token_updater.start()
    print('fetching token', end='', flush=True)
    for i in range(5):
        time.sleep(1)   # wait token to be updated
        print('.', end='', flush=True)
    print(' Successful!\n')

    # download works
    with ThreadPoolExecutor(max_workers=WORKER_NUM) as executor:
        future_to_page = {executor.submit(download, idx): idx for idx in tasks}
    
    undone_queue = queue.Queue()
    for future in as_completed(future_to_page):
        idx = future_to_page[future]
        try:
            if not future.result():
                undone_queue.put(idx)
        except Exception as exc:
            print('%d generated an exception: %s' % (idx, exc))
    
    # stop updating token
    token_updater.stop()

    # statistics
    print('\n\n' + '='*40 + '\nTask Complete!\n')
    print('Total download: {}'.format(len(tasks)))
    print('\tDone: {}'.format(done))
    print('\tFail: {}'.format(total - done))

    # write undones to file
    with open('fail.log', 'w+') as f:
        while not undone_queue.empty():
            idx = undone_queue.get()
            f.write(str(idx))
            f.write('\n')
