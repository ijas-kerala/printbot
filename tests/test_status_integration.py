
import sys
import os
import time
sys.path.append(os.getcwd())

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from web.models.models import Base, Job
from web.routers.status import get_machine_status
import datetime

def test_priority():
    # Setup In-Memory DB
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    db = Session()
    
    print("--- Test 1: Idle ---")
    status = get_machine_status(db)
    print(f"Status: {status['status']} | State: {status['state']}")
    assert status['state'] == "idle"

    print("\n--- Test 2: Single Printing Job ---")
    job1 = Job(id=1, status="printing", created_at=datetime.datetime.now(), total_cost=10.0, file_path="test.pdf", filename="test.pdf")
    db.add(job1)
    db.commit()
    
    status = get_machine_status(db)
    print(f"Status: {status['status']} | State: {status['state']}")
    assert status['state'] == "printing"
    assert "Job #1" in status['status']

    print("\n--- Test 3: New Upload while Printing (Race Condition) ---")
    # Add a newer job that is 'payment_pending'
    # In the old logic, this would overwrite the status because it's 'latest'
    job2 = Job(id=2, status="payment_pending", created_at=datetime.datetime.now() + datetime.timedelta(seconds=10), total_cost=5.0, file_path="new.pdf", filename="new.pdf")
    db.add(job2)
    db.commit()
    
    status = get_machine_status(db)
    print(f"Status: {status['status']} | State: {status['state']}")
    
    # CRITICAL CHECK: Should still be PRINTING job #1
    if status['state'] == "printing" and "Job #1" in status['status']:
        print("PASS: Priority logic works. Printing overrides new upload.")
    else:
        print(f"FAIL: Logic failed. State is {status['state']}")
        sys.exit(1)

    print("\n--- Test 4: Printing Finished ---")
    job1.status = "completed"
    db.commit()
    
    status = get_machine_status(db)
    print(f"Status: {status['status']} | State: {status['state']}")
    # Now it should show the new job
    assert status['state'] == "uploading"
    assert "Waiting for Payment" in status['status']
    print("PASS: Reverted to latest job after printing finished.")

if __name__ == "__main__":
    test_priority()
