import pyrebase4 as pyrebase

firebaseConfig = {
    "apiKey": "AIzaSyDRxbw6-kJQsXXXr0vpnlDqhaUWKOjmQIU", 
    "authDomain": "freight-demo2.firebaseapp.com",
    "projectId": "freight-demo2",
    "storageBucket": "freight-demo2.appspot.com",
    "messagingSenderId": "199645170835",
    "appId": "1:199645170835:web:efa8ff8d5b85416eb71166", 
    "databaseURL": ""
}

firebase = pyrebase.initialize_app(firebaseConfig)
auth = firebase.auth()
