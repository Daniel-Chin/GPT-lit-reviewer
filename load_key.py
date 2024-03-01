def loadKey():
    with open('key_location.txt', 'r', encoding='utf-8') as f:
        key_location = f.read().strip()
    with open(key_location, 'r', encoding='utf-8') as f:
        line = f.read().strip()
    return line.split('=')[1]

if __name__ == '__main__':
    print(loadKey())
