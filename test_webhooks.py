# test_webhooks.py

import requests
import time
import json

# Configuration
# The server must be running on localhost:3000 for this to work
BASE_URL = "http://localhost:3000"
EVENTS_URL = f"{BASE_URL}/events"
EVENTS2_URL = f"{BASE_URL}/events2"

# A consistent userId to simulate a single transaction session
TEST_USER_ID = "test-user-123"

# --- Test Case 1: Simulate a full transaction flow for the /events endpoint ---
def test_full_transaction_flow():
    """
    Sends a sequence of 6 events for the same user to test the
    session tracking and validation logic.
    """
    print("--- Starting Full Transaction Flow Test ---")
    
    # Define the sequence of statuses for a single transaction.
    # The last status "payout_successful" is what the checker looks for.
    transaction_statuses = [
        "deposit_awaiting",
        "deposit_successful",
        "processing_intermediate",
        "another_status_update",
        "payout_processing",
        "payout_successful"
    ]

    for i, status in enumerate(transaction_statuses):
        # Construct the payload for this step in the transaction
        payload = {
            "data": {
                "order": {
                    "userId": TEST_USER_ID,
                    "status": status
                }
            }
        }
        
        print(f"\nSending event {i+1}/{len(transaction_statuses)} with status: '{status}'")
        
        try:
            response = requests.post(EVENTS_URL, json=payload)
            
            # Raise an exception if the server returned an error (4xx or 5xx)
            response.raise_for_status()
            
            print(f"  -> Success! Server responded with: {response.json()}")
            
        except requests.exceptions.RequestException as e:
            print(f"  -> Error sending request: {e}")
        
        # Wait a moment between requests to simulate real events and make logs readable
        time.sleep(1)

    print("\n--- Full Transaction Flow Test Finished ---")
    print("Check your server logs for the final session validation result.")


# --- Test Case 2: Test the simpler /events2 endpoint ---
def test_simple_event():
    """
    Sends a single, simple event to the /events2 endpoint.
    """
    print("\n--- Starting Simple Event Test (/events2) ---")
    
    payload = {
        "eventType": "test.event",
        "message": "This is a simple test payload.",
        "data": {"key": "value"}
    }
    
    try:
        response = requests.post(EVENTS2_URL, json=payload)
        response.raise_for_status()
        print(f"  -> Success! Server responded with: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"  -> Error sending request: {e}")
    
    print("--- Simple Event Test Finished ---")


if __name__ == "__main__":
    # Run the tests in sequence
    test_full_transaction_flow()
    test_simple_event()
