"""
Demo script for the Task Manager API
This script demonstrates how to use the API endpoints
"""

import requests
import json

# API base URL (update if you change port)
API_URL = "http://127.0.0.1:5001"

def print_response(response, title):
    """Print formatted response"""
    print(f"\n{'='*50}")
    print(f" {title}")
    print(f"{'='*50}")
    try:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except json.decoder.JSONDecodeError:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

def demo_api():
    """Demonstrate API usage"""
    print("🚀 Task Manager API Demo")
    print(f"Make sure the API server is running on {API_URL}")
    print("You can start it with: python app_with_docs.py")
    
    input("\nPress Enter to continue...")
    
    try:
        # 1. Test home endpoint
        print("\n1. Testing home endpoint...")
        response = requests.get(f"{API_URL}/")
        print_response(response, "Home Endpoint")
        
        # 2. Register a new user
        print("\n2. Registering a new user...")
        user_data = {
            "username": "demo_user",
            "email": "demo@example.com",
            "password": "demo_password"
        }
        response = requests.post(f"{API_URL}/api/auth/register", json=user_data)
        print_response(response, "User Registration")
        
        if response.status_code != 201:
            print("❌ Registration failed. Trying to login with existing user...")
            login_data = {
                "username": "demo_user",
                "password": "demo_password"
            }
            response = requests.post(f"{API_URL}/api/auth/login", json=login_data)
            print_response(response, "User Login")
        
        # Extract access token
        token = response.json().get('access_token')
        if not token:
            print("❌ No access token received. Exiting...")
            return
        
        headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json"
        }
        
        # 3. Create a new task
        print("\n3. Creating a new task...")
        task_data = {
            "subject": "Complete API Demo",      # Correct field
            "description": "Finish demonstrating the Task Manager API",
            "completed": False
        }
        response = requests.post(f"{API_URL}/api/tasks", json=task_data, headers=headers)
        print_response(response, "Create Task")
        task_id = response.json().get('task', {}).get('id')
        
        # 4. Get all tasks
        print("\n4. Getting all tasks...")
        response = requests.get(f"{API_URL}/api/tasks", headers=headers)
        print_response(response, "Get All Tasks")
        
        # 5. Get specific task
        if task_id:
            print(f"\n5. Getting specific task (ID: {task_id})...")
            response = requests.get(f"{API_URL}/api/tasks/{task_id}", headers=headers)
            print_response(response, "Get Specific Task")
            
            # 6. Update task
            print(f"\n6. Updating task (ID: {task_id})...")
            update_data = {
                "subject": "Updated: Complete API Demo",
                "description": "Updated description",
                "completed": True
            }
            response = requests.put(f"{API_URL}/api/tasks/{task_id}", json=update_data, headers=headers)
            print_response(response, "Update Task")
            
            # 7. Get updated task
            print(f"\n7. Getting updated task (ID: {task_id})...")
            response = requests.get(f"{API_URL}/api/tasks/{task_id}", headers=headers)
            print_response(response, "Get Updated Task")
            
            # 8. Create another task
            print("\n8. Creating another task...")
            task_data2 = {
                "subject": "Test Task 2",
                "description": "This is a second task",
                "completed": False
            }
            response = requests.post(f"{API_URL}/api/tasks", json=task_data2, headers=headers)
            print_response(response, "Create Second Task")
            
            # 9. Get all tasks again
            print("\n9. Getting all tasks after creating second task...")
            response = requests.get(f"{API_URL}/api/tasks", headers=headers)
            print_response(response, "Get All Tasks (After Second Task)")
            
            # 10. Delete first task
            print(f"\n10. Deleting first task (ID: {task_id})...")
            response = requests.delete(f"{API_URL}/api/tasks/{task_id}", headers=headers)
            print_response(response, "Delete Task")
            
            # 11. Get remaining tasks
            print("\n11. Getting remaining tasks...")
            response = requests.get(f"{API_URL}/api/tasks", headers=headers)
            print_response(response, "Get Remaining Tasks")
        
        print("\n✅ Demo completed successfully!")
        print(f"\n📚 For interactive documentation, visit: {API_URL}/docs/")
        
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API server.")
        print(f"Make sure the server is running with: python app_with_docs.py")
    except Exception as e:
        print(f"❌ An error occurred: {e}")

if __name__ == "__main__":
    demo_api()