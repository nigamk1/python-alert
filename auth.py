import json
import webbrowser
import requests
from urllib.parse import urlparse, parse_qs
import os

class UpstoxAuth:
    def __init__(self, config_path="config.json"):
        """Initialize with config file containing API credentials"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        self.client_id = config['upstox']['client_id']
        self.client_secret = config['upstox']['client_secret']
        self.redirect_uri = config['upstox']['redirect_uri']
        self.refresh_token_file = "upstox_refresh.json"
    
    def get_login_url(self):
        """Generate login URL for Upstox authorization"""
        login_url = (
            f"https://api.upstox.com/v2/login/authorization/dialog?"
            f"response_type=code&"
            f"client_id={self.client_id}&"
            f"redirect_uri={self.redirect_uri}"
        )
        return login_url
    
    def open_login_browser(self):
        """Open login URL in browser"""
        login_url = self.get_login_url()
        print(f"Opening login URL: {login_url}")
        webbrowser.open(login_url)
        print("\n1. Login to Upstox in the browser")
        print("2. After successful login, you'll be redirected to a URL")
        print("3. Copy the complete redirect URL and paste it below")
        
    def extract_request_token(self, redirect_url):
        """Extract request token from redirect URL"""
        try:
            parsed_url = urlparse(redirect_url)
            query_params = parse_qs(parsed_url.query)
            request_token = query_params.get('code', [None])[0]
            
            if not request_token:
                raise ValueError("Request token not found in URL")
                
            return request_token
        except Exception as e:
            raise ValueError(f"Failed to extract request token: {str(e)}")
    
    def exchange_token(self, request_token):
        """Exchange request token for access token and refresh token"""
        url = "https://api.upstox.com/v2/login/authorization/token"
        
        headers = {
            'accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        data = {
            'code': request_token,
            'client_id': self.client_id,
            'client_secret': self.client_secret,
            'redirect_uri': self.redirect_uri,
            'grant_type': 'authorization_code',
        }
        
        try:
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Debug: Print the actual response to understand what we're getting
            print(f"📝 API Response: {json.dumps(token_data, indent=2)}")
            
            if 'access_token' not in token_data:
                raise ValueError("Access token not received")
                
            return token_data
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Token exchange failed: {str(e)}")
    
    def save_refresh_token(self, token_data):
        """Save refresh token to file"""
        # Handle cases where refresh_token might not be present
        refresh_token = token_data.get('refresh_token')
        access_token = token_data.get('access_token')
        
        if not access_token:
            raise ValueError("Access token not found in response")
        
        refresh_data = {
            'access_token': access_token
        }
        
        # Only add refresh_token if it exists
        if refresh_token:
            refresh_data['refresh_token'] = refresh_token
            print("✅ Refresh token found and saved")
        else:
            print("⚠️ No refresh token in response - using access token only")
            # Some Upstox configurations might not provide refresh tokens
            # In this case, we'll need to re-authenticate when the token expires
        
        with open(self.refresh_token_file, 'w') as f:
            json.dump(refresh_data, f, indent=2)
        
        print(f"✅ Token data saved to {self.refresh_token_file}")
    
    def load_refresh_token(self):
        """Load refresh token from file"""
        if not os.path.exists(self.refresh_token_file):
            raise FileNotFoundError(f"{self.refresh_token_file} not found. Run initial authentication first.")
        
        with open(self.refresh_token_file, 'r') as f:
            return json.load(f)
    
    def refresh_access_token(self):
        """Use refresh token to get new access token"""
        try:
            token_data = self.load_refresh_token()
            
            # Check if we have a refresh token
            if 'refresh_token' not in token_data:
                print("⚠️ No refresh token available. Re-authentication required.")
                return token_data.get('access_token')  # Return existing access token if available
            
            refresh_token = token_data['refresh_token']
            
            url = "https://api.upstox.com/v2/login/authorization/token"
            
            headers = {
                'accept': 'application/json',
                'Content-Type': 'application/x-www-form-urlencoded',
            }
            
            data = {
                'refresh_token': refresh_token,
                'client_id': self.client_id,
                'client_secret': self.client_secret,
                'grant_type': 'refresh_token',
            }
            
            response = requests.post(url, headers=headers, data=data)
            response.raise_for_status()
            
            new_token_data = response.json()
            
            # Update stored tokens
            updated_data = {
                'access_token': new_token_data['access_token']
            }
            
            # Keep the refresh token (it might be the same or a new one)
            if 'refresh_token' in new_token_data:
                updated_data['refresh_token'] = new_token_data['refresh_token']
            else:
                updated_data['refresh_token'] = refresh_token  # Keep the old one
            
            with open(self.refresh_token_file, 'w') as f:
                json.dump(updated_data, f, indent=2)
            
            print("✅ Access token refreshed successfully")
            return new_token_data['access_token']
            
        except Exception as e:
            raise Exception(f"Failed to refresh access token: {str(e)}")

def get_access_token():
    """Get valid access token (refresh if needed)"""
    auth = UpstoxAuth()
    try:
        return auth.refresh_access_token()
    except FileNotFoundError:
        print("❌ Token file not found. Please run initial authentication first.")
        return None
    except Exception as e:
        print(f"❌ Error getting access token: {str(e)}")
        print("💡 If refresh token is not available, you may need to re-authenticate.")
        print("   Run: python auth.py")
        return None

def main():
    """Initial authentication flow"""
    print("🚀 Upstox Authentication Setup")
    print("=" * 40)
    
    auth = UpstoxAuth()
    
    # Step 1: Open login URL
    auth.open_login_browser()
    
    # Step 2: Get redirect URL from user
    redirect_url = input("\nPaste the complete redirect URL here: ").strip()
    
    try:
        # Step 3: Extract request token
        request_token = auth.extract_request_token(redirect_url)
        print(f"✅ Request token extracted: {request_token[:20]}...")
        
        # Step 4: Exchange for access token
        print("🔄 Exchanging tokens...")
        token_data = auth.exchange_token(request_token)
        print("✅ Token exchange successful!")
        
        # Step 5: Save refresh token
        auth.save_refresh_token(token_data)
        
        print("\n🎉 Authentication setup complete!")
        print("You can now run main.py to start the EMA alerts system.")
        
    except Exception as e:
        print(f"❌ Authentication failed: {str(e)}")
        print("Please try again or check your credentials.")

if __name__ == "__main__":
    main()
