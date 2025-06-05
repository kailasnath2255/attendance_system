import re
import logging
import platform
import subprocess

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def normalize_mac(mac_address):
    """Normalize MAC address to lowercase with colons"""
    if not mac_address:
        return None
    # Remove any separators and convert to lowercase
    clean_mac = re.sub(r'[^a-fA-F0-9]', '', mac_address.lower())
    # Insert colons
    if len(clean_mac) == 12:  # Valid MAC address should be 12 hex chars
        formatted_mac = ':'.join(clean_mac[i:i+2] for i in range(0, len(clean_mac), 2))
        return formatted_mac
    return None

def get_wifi_bssid():
    """Get WiFi BSSID (MAC address of the connected router/access point)"""
    try:
        os_name = platform.system()
        
        if os_name == "Windows":
            # Windows command to get current WiFi info
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode('utf-8', errors='ignore')
            # Look for BSSID
            bssid_match = re.search(r"BSSID\s+:\s(.*)", output)
            if not bssid_match:
                # Try alternative format
                bssid_match = re.search(r"AP BSSID\s+:\s(.*)", output)
                
            if bssid_match:
                return normalize_mac(bssid_match.group(1).strip())
                
        elif os_name == "Darwin":  # macOS
            # macOS command to get current WiFi info
            try:
                output = subprocess.check_output("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I", shell=True).decode('utf-8', errors='ignore')
                bssid_match = re.search(r"\s+BSSID:\s(.*)", output)
                
                if bssid_match:
                    return normalize_mac(bssid_match.group(1).strip())
            except:
                logger.error("Failed to get BSSID on macOS")
                
        elif os_name == "Linux":
            try:
                # First method: Using iwconfig to get BSSID (Access Point)
                output = subprocess.check_output("iwconfig 2>/dev/null | grep 'Access Point'", shell=True).decode('utf-8', errors='ignore')
                bssid_match = re.search(r"Access Point:\s+([0-9A-Fa-f:]+)", output)
                if bssid_match:
                    return normalize_mac(bssid_match.group(1).strip())
                    
                # Second method: Using iw dev
                output = subprocess.check_output("iw dev | grep -A 5 Interface | grep -o ..:..:..:..:..:..", shell=True).decode('utf-8', errors='ignore')
                if output.strip():
                    return normalize_mac(output.strip())
            except:
                logger.error("Failed to get BSSID on Linux")
        
        logger.warning("Could not determine BSSID using system commands")
        return None
    except Exception as e:
        logger.error(f"Error getting WiFi BSSID: {e}")
        return None

def get_current_wifi_info():
    """Get current WiFi connection information"""
    try:
        os_name = platform.system()
        result = {'ssid': None, 'bssid': None}
        
        if os_name == "Windows":
            # Windows command to get current WiFi info
            output = subprocess.check_output("netsh wlan show interfaces", shell=True).decode('utf-8', errors='ignore')
            
            # Check SSID
            ssid_match = re.search(r"SSID\s+:\s(.*)", output)
            bssid_match = re.search(r"BSSID\s+:\s(.*)", output)
            
            # Try alternative format if not found
            if not bssid_match:
                bssid_match = re.search(r"AP BSSID\s+:\s(.*)", output)
            
            if ssid_match:
                result['ssid'] = ssid_match.group(1).strip()
            
            if bssid_match:
                result['bssid'] = normalize_mac(bssid_match.group(1).strip())
                
        elif os_name == "Darwin":  # macOS
            # macOS command to get WiFi info
            try:
                output = subprocess.check_output("/System/Library/PrivateFrameworks/Apple80211.framework/Versions/Current/Resources/airport -I", shell=True).decode('utf-8', errors='ignore')
                
                # Check SSID
                ssid_match = re.search(r"\s+SSID:\s(.*)", output)
                bssid_match = re.search(r"\s+BSSID:\s(.*)", output)
                
                if ssid_match:
                    result['ssid'] = ssid_match.group(1).strip()
                
                if bssid_match:
                    result['bssid'] = normalize_mac(bssid_match.group(1).strip())
            except:
                logger.error("Failed to get WiFi info on macOS")
                
        elif os_name == "Linux":
            # Get SSID
            try:
                output = subprocess.check_output("iwgetid -r", shell=True).decode('utf-8', errors='ignore')
                result['ssid'] = output.strip()
            except:
                logger.error("Failed to get SSID on Linux")
            
            # Get BSSID
            try:
                output = subprocess.check_output("iwconfig 2>/dev/null | grep 'Access Point'", shell=True).decode('utf-8', errors='ignore')
                bssid_match = re.search(r"Access Point:\s+([0-9A-Fa-f:]+)", output)
                if bssid_match:
                    result['bssid'] = normalize_mac(bssid_match.group(1).strip())
            except:
                logger.error("Failed to get BSSID on Linux")
        
        # If we couldn't get the BSSID, try dedicated method
        if not result['bssid']:
            result['bssid'] = get_wifi_bssid()
            
        return result
        
    except Exception as e:
        logger.error(f"Error getting WiFi info: {e}")
        return {'ssid': None, 'bssid': None}

def check_wifi_connection(conn):
    """
    Check if connected to the allowed college WiFi access point
    
    Args:
        conn: Database connection
        
    Returns:
        dict: Connection status and details
    """
    # Get current WiFi information
    wifi_info = get_current_wifi_info()
    
    # Get allowed access points from database
    allowed_ap = conn.execute('SELECT bssid FROM allowed_access_points').fetchone()
    
    result = {
        'connected': False,
        'ssid': wifi_info.get('ssid'),
        'bssid': wifi_info.get('bssid'),
        'required_bssid': allowed_ap['bssid'] if allowed_ap else None,
        'message': "Not connected to the required WiFi access point"
    }
    
    # If BSSID matches the allowed AP
    if result['bssid'] and allowed_ap and normalize_mac(result['bssid']) == normalize_mac(allowed_ap['bssid']):
        result['connected'] = True
        result['message'] = "Connected to the approved WiFi access point"
    
    return result

def verify_college_wifi(conn):
    """
    Simple wrapper for check_wifi_connection for backward compatibility
    """
    return check_wifi_connection(conn)