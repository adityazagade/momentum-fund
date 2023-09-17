class AppConfig:
    def __init__(self, properties_file):
        self.properties = {}
        with open(properties_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and '=' in line:
                    key, value = line.split('=', 1)
                    self.properties[key.strip()] = value.strip()

    def get(self, key):
        return self.properties.get(key)

    def set(self, key, value):
        self.properties[key] = value

    def write(self):
        with open('app.properties', 'w') as f:
            for key, value in self.properties.items():
                f.write(f'{key}={value}\n')

    def get_or_default(self, key, default):
        return self.properties.get(key, default)
