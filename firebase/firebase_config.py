import pyrebase

config = {
  "apiKey": "AIzaSyDRxbw6-kJQsXXXr0vpnlDqhaUWKOjmQIU",
  "authDomain": "freight-demo2.firebaseapp.com",
  "databaseURL": "https://freight-demo2.firebaseio.com",
  "storageBucket": "freight-demo2.firebasestorage.app"
}

firebase = pyrebase.initialize_app(config)
auth = firebase.auth()
db = firebase.database()
