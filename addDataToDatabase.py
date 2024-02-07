import firebase_admin
from firebase_admin import credentials
from firebase_admin import db

cred = credentials.Certificate("serviceAccountKey.json")
firebase_admin.initialize_app(cred, {
    "databaseURL": "https://attendance-system-ab9c9-default-rtdb.firebaseio.com/"
})

ref = db.reference("Users")

data = {
    "312654":
        {
            "name": "Mutazar Hassan",
            "major": "Robotics",
            "starting_year": 2017,
            "total_attendance": 6,
            "standing": "Good",
            "year": 4,
            "last_attendance_time": "2022-12-11 10:54:34"
        },
    "85271":
            {
                "name": "Emily Blunt",
                "major": "Robotics",
                "starting_year": 2017,
                "total_attendance": 6,
                "standing": "Good",
                "year": 4,
                "last_attendance_time": "2022-12-11 10:54:34"
            },
    "963852":
            {
                "name": "Elon Musk",
                "major": "Robotics",
                "starting_year": 2017,
                "total_attendance": 6,
                "standing": "Good",
                "year": 4,
                "last_attendance_time": "2022-12-11 10:54:34"
            }
}


for key, value in data.items():
    ref.child(key).set(value)