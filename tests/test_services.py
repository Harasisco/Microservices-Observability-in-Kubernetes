import requests, hashlib, time

def wait(url):
    for _ in range(30):
        try:
            requests.get(url, timeout=1)
            print(f"✅ {url} is ready")
            return
        except requests.exceptions.ConnectionError:
            time.sleep(1)
    raise RuntimeError(f"❌ Service {url} never became ready")

wait("http://localhost:8080/health")
wait("http://localhost:8081/health")

def test_hash():
    msg = "Apple"
    exp = hashlib.sha256(msg.encode()).hexdigest()
    resp = requests.post("http://localhost:8080/hash", data=msg)
    got = resp.json()["hash"]
    
    print(f"\n🔍 Testing /hash")
    print(f"Input: {msg}")
    print(f"Expected hash: {exp}")
    print(f"Received hash: {got}")
    
    assert got == exp, "❌ Hash mismatch!"
    print("✅ Hash test passed")

def test_length():
    msg = "Banana"
    resp = requests.post("http://localhost:8081/length", data=msg)
    got = resp.json()["length"]

    print(f"\n🔍 Testing /length")
    print(f"Input: {msg}")
    print(f"Expected length: {len(msg)}")
    print(f"Received length: {got}")

    assert got == len(msg), "❌ Length mismatch!"
    print("✅ Length test passed")

if __name__ == "__main__":
    test_hash()
    test_length()
    print("\n✅ All tests passed")
