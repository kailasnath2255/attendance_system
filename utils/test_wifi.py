import sqlite3
from wifi_checker import verify_college_wifi, check_wifi_connection

def get_db_connection():
    conn = sqlite3.connect('../database/attendance.db')
    conn.row_factory = sqlite3.Row
    return conn

if __name__ == "__main__":
    print("=== WiFi Connection Test ===")
    
    # First test simple WiFi checking
    print("\nTesting direct WiFi check:")
    ssid = input("Enter the SSID to check for: ")
    result = check_wifi_connection(ssid)
    
    print(f"\nConnection to {ssid}:")
    print(f"Connected: {result['connected']}")
    print(f"Current SSID: {result.get('ssid')}")
    print(f"Current BSSID: {result.get('bssid')}")
    
    # Test database-driven WiFi check
    print("\nTesting college WiFi verification:")
    try:
        conn = get_db_connection()
        wifi_result = verify_college_wifi(conn)
        
        print("\nCollege WiFi Verification Result:")
        print(f"Connected: {wifi_result['connected']}")
        print(f"Required SSID: {wifi_result.get('required_ssid')}")
        print(f"Current SSID: {wifi_result.get('ssid')}")
        print(f"Current BSSID: {wifi_result.get('bssid')}")
        print(f"Access Point: {wifi_result.get('access_point')}")
        print(f"Message: {wifi_result.get('message', 'No message')}")
        
        conn.close()
    except Exception as e:
        print(f"Error testing database connection: {e}")