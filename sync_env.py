import os

def sync_keys():
    # Read .env.example
    with open('.env.example', 'r') as f:
        example_lines = f.readlines()
    
    # Read .env
    if os.path.exists('.env'):
        with open('.env', 'r') as f:
            env_lines = f.readlines()
    else:
        env_lines = []

    # Parse .env keys
    env_keys = set()
    for line in env_lines:
        if '=' in line:
            key = line.split('=')[0].strip()
            env_keys.add(key)

    # Append missing keys from example
    with open('.env', 'a') as f:
        if env_lines and not env_lines[-1].endswith('\n'):
            f.write('\n')
        
        for line in example_lines:
            if '=' in line:
                key = line.split('=')[0].strip()
                if key not in env_keys:
                    f.write(line)
                    print(f"Added {key} to .env")

if __name__ == "__main__":
    sync_keys()
