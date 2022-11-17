# Fitting-System


## Requirements

- tkinter
- cv2
- os
- pymysql
- PIL
- RPi

## Preparation

Please download the [cv libaray](https://github.com/opencv/opencv/tree/master/data/haarcascades) which contains trained classifiers for detecting objects of a particular type

```
  haarcascade_frontalface_default.xml
  haarcascade_lowerbody.xml
  haarcascade_upperbody.xml
```

Please store the clothing information (`*.txt` files) in your mysql databased,
for example:


| Cloth Name (Str) | Size (Str)| Price (Str)|
|------------------|-----------|------------|
|史努比印花T恤-06-男 |S          | 299/活動價233|

Please change the connection inside the `pi.py` file (function `dbconnect()`)

```
def dbconnect():
	db = mysql.connect(host = '________(Your database IP)',
	port= _________(Your port),
	user = ________(The username of databased),
	passwd = _________(The passward of databased),
	db = "cloth" (The databased that you store the clothin information),
	charset = 'utf8')
	global cursor
	cursor = db.cursor()
  
```

## System Implementation

- For quickly start, please run file `python pi.py`

### Demo vedio

[![Watch the video](https://user-images.githubusercontent.com/83267883/202080585-17c5df52-91a0-4ecd-988b-6b3fcc7a9a23.jpg)](https://youtu.be/_9RW9zvGyAQ)

