# archive-book-downloader
A simple script to download borrowed books in Internet Archive

Click here to access [Internet Archive](https://archive.org/)

# Dependency

- Python 3
- requests

# Preparation

You need an Internet Archive **account** that can borrow books.

# Instruction

1. install python 3

2. clone this repository, and in the project root:
```shell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

3. set directory to save the book in the source code:
```python
SAVE_PATH = 'set your own save path'
```

4. borrow the book you want to download

5. get the `cookie` and `request example`. see [How to get cookie and request example](#t)

6. start downloading
```shell
python src\download.py [options]
```
There 3 pairs of options you can use:
- c/i: use **Cached** cookie and request example OR let user **Input** cookie and request example [**default**]
- r/n: **Restore** to downlaod pages in `fail.log` OR download a **New** book with a page range [**default**]
- p/d: use **Proxy** to download [**default**] OR **Directly** download

here are some examples:
```shell
python src\download.py        (download a new book)
python src\download.py cr     (download pages that weren't download correctly last time)
python src\download.py d      (download without using proxy)
```

**NOTE**: Using proxy is set by DEFAULT. You can config your proxy in the source code:
```python
PROXY = {
    'http': 'http://127.0.0.1:4780', # replace with your own proxy
    'https': 'http://127.0.0.1:4780', # replace with your own proxy
}
```
So, If you don't want to use proxy, don't forget to add option `d` in the command.

7. if you download a new book, for example, you type `python src\download.py` in the command line. You will be asked to input cookie and request example:
```
cookie > (you paste your cookie here)
request example > (you paste your request example url here)
page range > (you type your the page range here [format: begin-end]. note that the `begin` can be omit)
```
Then, the script will start downloading. You can take a cup of coffee till it finishes.

# How to get cookie and request example<span id="t"></span>

1. click `borrow` to borrow the book you want to download
2. press `F12` to open the develop tools
3. click column `Network`
4. go to a certain page and you'll see some connections showing in the develop tools
5. click one of the connection that fetching one page, and you'll see the `cookie` and `Request URL`
6. that's it. well done. If you don't understand see [Demos > get cookie and request example](#d)

# Customize

here are some variables you can customize:

```python
WORKER_NUM = 6 # number of downloading threads
REQUEST_TIMEOUT = 8 # request timeout
TOKEN_INTV = 120 # interval time for getting token
DOWNLOAD_INTV = 0.1 # interval time between two downloads in one thread
```

# Demos

## get cookie and request example<span id="d"></span>

1. borrow book

![image](https://user-images.githubusercontent.com/47183462/170027317-09680f29-d9b5-457d-bc28-c32c1581ebef.png)

2. press `F12` > `Network`. Jump to a certain page as we want to see some connections.

![image](https://user-images.githubusercontent.com/47183462/170028140-7df10c1c-52f6-4294-a7d5-be35878b996c.png)

3. click one connection to get `cookie` and `Request URL`

![image](https://user-images.githubusercontent.com/47183462/170028627-13c2b268-faa8-46d4-8072-c7c182d7019b.png)

## downlaod a book

set the save path, paste the cookies and request url, and start downloading

![image](https://user-images.githubusercontent.com/47183462/170030100-5f9d6102-0415-4d9f-970b-92cecb8d1a38.png)

then you'll get all the pages download

![image](https://user-images.githubusercontent.com/47183462/170031264-c8da0b0f-46e3-4c27-a8bf-a4075451a9be.png)

# Ending

Now you have all the images of the book. I recommend you to use [Cover](https://www.microsoft.com/store/productId/9WZDNCRFJ9W7) to read the book, which can be found in Microsoft Store easily.

![image](https://user-images.githubusercontent.com/47183462/170032987-b27e7e31-1858-48e7-b608-5aca5828ffb3.png)

Hope you enjoy your reading. 

# Respect for all the writers and their priceless masterpiece!
