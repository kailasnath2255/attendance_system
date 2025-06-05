DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS students;
DROP TABLE IF EXISTS attendance;
DROP TABLE IF EXISTS settings;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('admin', 'student'))
);

CREATE TABLE students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    name TEXT NOT NULL,
    roll_number TEXT UNIQUE NOT NULL,
    email TEXT UNIQUE NOT NULL,
    image_path TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users (id)
);

CREATE TABLE attendance (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id INTEGER NOT NULL,
    date TEXT NOT NULL,
    time TEXT NOT NULL,
    FOREIGN KEY (student_id) REFERENCES students (id),
    UNIQUE (student_id, date)
);

CREATE TABLE settings (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    wifi_ssid TEXT NOT NULL,
    wifi_password TEXT NOT NULL
);

-- Add new table to store allowed access points
CREATE TABLE IF NOT EXISTS allowed_access_points (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ssid TEXT NOT NULL,
    bssid TEXT NOT NULL,  -- MAC address of the access point
    description TEXT,     -- Optional description (e.g., "Library AP", "Classroom Building")
    UNIQUE(bssid)
);

-- Insert some example access points (you'll replace these with your actual college APs)
INSERT OR IGNORE INTO allowed_access_points (ssid, bssid, description) 
VALUES 
    ('College_WiFi', '00:11:22:33:44:55', 'Main Building - Floor 1'),
    ('College_WiFi', '00:11:22:33:44:56', 'Main Building - Floor 2'),
    ('College_WiFi', '00:11:22:33:44:57', 'Library'),
    ('College_WiFi', '00:11:22:33:44:58', 'Science Building'),
    ('BSNL_Suresh','48-A4-72-7B-72-8F', 'home');

