import asyncio
import aiohttp
import random
import time
from typing import List, Dict, Any
import json
from concurrent.futures import ThreadPoolExecutor
import statistics

class StressTestRunner:
    def __init__(self, base_url: str = "http://localhost:5000"):
        self.base_url = base_url
        self.session = None
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup_database()
        if self.session:
            await self.session.close()
    
    async def cleanup_database(self):
        """Clean up all reservations from the database"""
        try:
            print("Cleaning up database...")
            all_seats = list(range(1, 109))
            result = await self.cancel_reservations(all_seats)
            if result.get('status') in [200, 404]:  
                print("Database cleanup completed")
            else:
                print(f"Database cleanup warning: {result}")
        except Exception as e:
            print(f"Database cleanup error (non-critical): {e}")
    
    async def make_reservation(self, seat_id: int, user: str) -> Dict[str, Any]:
        """Make a reservation request"""
        try:
            async with self.session.post(
                f"{self.base_url}/book",
                json={"seat_id": seat_id, "user": user},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return {
                    "status": response.status,
                    "data": await response.json(),
                    "seat_id": seat_id,
                    "user": user,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "seat_id": seat_id,
                "user": user,
                "timestamp": time.time()
            }
    
    async def update_reservation(self, seat_id: int, user: str) -> Dict[str, Any]:
        """Update a reservation request"""
        try:
            async with self.session.put(
                f"{self.base_url}/book",
                json={"seat_id": seat_id, "user": user},
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return {
                    "status": response.status,
                    "data": await response.json(),
                    "seat_id": seat_id,
                    "user": user,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "seat_id": seat_id,
                "user": user,
                "timestamp": time.time()
            }
    
    async def cancel_reservations(self, seat_ids: List[int]) -> Dict[str, Any]:
        """Cancel reservations"""
        try:
            async with self.session.post(
                f"{self.base_url}/cancel",
                json={"seat_id_tab": seat_ids},
                timeout=aiohttp.ClientTimeout(total=15)
            ) as response:
                return {
                    "status": response.status,
                    "data": await response.json(),
                    "seat_ids": seat_ids,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "seat_ids": seat_ids,
                "timestamp": time.time()
            }
    
    async def get_reservations(self) -> Dict[str, Any]:
        """Get all reservations"""
        try:
            async with self.session.get(
                f"{self.base_url}/",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return {
                    "status": response.status,
                    "timestamp": time.time()
                }
        except Exception as e:
            return {
                "status": 0,
                "error": str(e),
                "timestamp": time.time()
            }

    def analyze_results(self, results: List[Dict[str, Any]], test_name: str):
        """Analyze and print test results"""
        print(f"\n{'='*60}")
        print(f"STRESS TEST RESULTS: {test_name}")
        print(f"{'='*60}")
        
        total_requests = len(results)
        successful_requests = len([r for r in results if r.get('status', 0) in [200, 201]])
        failed_requests = len([r for r in results if r.get('status', 0) not in [200, 201, 409, 404]])
        conflict_requests = len([r for r in results if r.get('status', 0) == 409])
        not_found_requests = len([r for r in results if r.get('status', 0) == 404])
        
        print(f"Total Requests: {total_requests}")
        print(f"Successful (200/201): {successful_requests}")
        print(f"Conflicts (409): {conflict_requests}")
        print(f"Not Found (404): {not_found_requests}")
        print(f"Failed/Errors: {failed_requests}")
        print(f"Success Rate: {(successful_requests/total_requests)*100:.2f}%")
        
        timestamps = [r['timestamp'] for r in results if 'timestamp' in r]
        if len(timestamps) > 1:
            duration = max(timestamps) - min(timestamps)
            print(f"Test Duration: {duration:.2f} seconds")
            print(f"Requests per Second: {total_requests/duration:.2f}")
        
        status_codes = {}
        for result in results:
            status = result.get('status', 0)
            status_codes[status] = status_codes.get(status, 0) + 1
        
        print(f"Status Code Breakdown: {status_codes}")
        
        errors = [r for r in results if 'error' in r]
        if errors:
            print(f"\nSample Errors (showing first 3):")
            for error in errors[:3]:
                print(f"  - {error.get('error', 'Unknown error')}")

async def stress_test_1_rapid_requests():
    """Stress Test 1: The client makes the same request very quickly"""
    print("Starting Stress Test 1: Rapid Same Requests")
    
    async with StressTestRunner() as runner:
        seat_id = 50
        user = "rapid_user"
        
        tasks = []
        for i in range(100):
            tasks.append(runner.make_reservation(seat_id, user))
        
        start_time = time.time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = time.time()
        
        processed_results = []
        for result in results:
            if isinstance(result, Exception):
                processed_results.append({
                    "status": 0,
                    "error": str(result),
                    "timestamp": time.time()
                })
            else:
                processed_results.append(result)
        
        runner.analyze_results(processed_results, "Rapid Same Requests")
        print(f"Time taken: {end_time - start_time:.2f} seconds")

async def stress_test_2_random_requests():
    """Stress Test 2: Two or more clients make random requests"""
    print("\nStarting Stress Test 2: Multiple Clients Random Requests")
    
    async def client_worker(client_id: int, num_requests: int):
        async with StressTestRunner() as runner:
            results = []
            for i in range(num_requests):
                operation = random.choice(['book', 'update', 'cancel'])
                seat_id = random.randint(1, 108)
                user = f"client_{client_id}_user_{i}"
                
                if operation == 'book':
                    result = await runner.make_reservation(seat_id, user)
                elif operation == 'update':
                    result = await runner.update_reservation(seat_id, user)
                else:  
                    cancel_seats = [random.randint(1, 108) for _ in range(random.randint(1, 5))]
                    result = await runner.cancel_reservations(cancel_seats)
                
                results.append(result)
                
                await asyncio.sleep(random.uniform(0.01, 0.1))
            
            return results
    
    client_tasks = []
    for client_id in range(5):
        client_tasks.append(client_worker(client_id, 50))
    
    start_time = time.time()
    client_results = await asyncio.gather(*client_tasks)
    end_time = time.time()
    
    all_results = []
    for client_result in client_results:
        all_results.extend(client_result)
    
    StressTestRunner().analyze_results(all_results, "Multiple Clients Random Requests")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

async def stress_test_3_seat_race():
    """Stress Test 3: Two clients try to occupy all seats simultaneously"""
    print("\nStarting Stress Test 3: Seat Occupation Race")
    
    async def client_seat_grabber(client_id: int):
        async with StressTestRunner() as runner:
            results = []
            tasks = []

            seats_to_book = list(range(1, 109))
            random.seed(2 * client_id)
            random.shuffle(seats_to_book)
            for seat_id in seats_to_book:
                user = f"client_{client_id}"
                tasks.append(runner.make_reservation(seat_id, user))
            
            seat_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for result in seat_results:
                if isinstance(result, Exception):
                    results.append({
                        "status": 0,
                        "error": str(result),
                        "timestamp": time.time()
                    })
                else:
                    results.append(result)
            
            return results
    
    start_time = time.time()
    client1_task = client_seat_grabber(1)
    client2_task = client_seat_grabber(2)
    
    client1_results, client2_results = await asyncio.gather(client1_task, client2_task)
    end_time = time.time()
    
    print(f"Client 1 successful bookings: {len([r for r in client1_results if r.get('status') == 201])}")
    print(f"Client 2 successful bookings: {len([r for r in client2_results if r.get('status') == 201])}")
    
    all_results = client1_results + client2_results
    StressTestRunner().analyze_results(all_results, "Seat Occupation Race")
    print(f"Time taken: {end_time - start_time:.2f} seconds")

async def stress_test_4_constant_churn():
    """Stress Test 4: Constant cancellations and seat occupancy"""
    print("\nStarting Stress Test 4: Constant Churn (Book/Cancel)")
    
    async with StressTestRunner() as runner:
        results = []
        start_time = time.time()
        duration = 5  
        
        async def booking_worker():
            worker_results = []
            while time.time() - start_time < duration:
                seat_id = random.randint(1, 108)
                user = f"churn_user_{random.randint(1, 100)}"
                result = await runner.make_reservation(seat_id, user)
                worker_results.append(result)
                await asyncio.sleep(0.1)
            return worker_results
        
        async def cancellation_worker():
            worker_results = []
            while time.time() - start_time < duration:
                seats_to_cancel = [random.randint(1, 108) for _ in range(random.randint(1, 10))]
                result = await runner.cancel_reservations(seats_to_cancel)
                worker_results.append(result)
                await asyncio.sleep(0.2)
            return worker_results
        
        booking_tasks = [booking_worker() for _ in range(3)]  
        cancellation_tasks = [cancellation_worker() for _ in range(2)]  
        
        all_tasks = booking_tasks + cancellation_tasks
        task_results = await asyncio.gather(*all_tasks)
        
        for task_result in task_results:
            results.extend(task_result)
        
        runner.analyze_results(results, "Constant Churn")

async def stress_test_5_large_group_cancellation():
    """Stress Test 5: Make large group cancellation of many reservations"""
    print("\nStarting Stress Test 5: Large Group Cancellations")
    
    async with StressTestRunner() as runner:
        print("Setting up reservations...")
        setup_tasks = []
        for seat_id in range(1, 109):
            user = f"setup_user_{seat_id}"
            setup_tasks.append(runner.make_reservation(seat_id, user))
        
        setup_results = await asyncio.gather(*setup_tasks, return_exceptions=True)
        successful_setups = len([r for r in setup_results if not isinstance(r, Exception) and r.get('status') == 201])
        print(f"Set up {successful_setups} reservations")
        
        results = []
        
        cancellation_size = 100

        for _ in range(5):  
            seats_to_cancel = random.sample(range(1, 109), cancellation_size)
            result = await runner.cancel_reservations(seats_to_cancel)
            results.append(result)
            await asyncio.sleep(1)
        
        runner.analyze_results(results, "Large Group Cancellations")

async def run_all_stress_tests():
    """Run all stress tests sequentially"""
    print("Starting Comprehensive Stress Test Suite")
    print("=" * 60)
    
    async with StressTestRunner() as initial_cleanup:
            await initial_cleanup.cleanup_database()

    try:
        await stress_test_1_rapid_requests()
        await asyncio.sleep(2)  
        
        await stress_test_2_random_requests()
        await asyncio.sleep(2)
        
        await stress_test_3_seat_race()
        await asyncio.sleep(2)
        
        await stress_test_4_constant_churn()
        await asyncio.sleep(2)
        
        await stress_test_5_large_group_cancellation()
        
    except Exception as e:
        print(f"Error during stress testing: {e}")
    
    print("\n" + "=" * 60)
    print("All stress tests completed!")
    print("=" * 60)

if __name__ == "__main__":
    print("Press Ctrl+C to cancel, or Enter to continue...")
    input()
    
    asyncio.run(run_all_stress_tests())
