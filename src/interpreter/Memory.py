class Memory:
    def __init__(self, name):
        self.name = name
        self.variables = {}

    def has_key(self, name):
        return name in self.variables

    def get(self, name):
        return self.variables.get(name)

    def put(self, name, value):
        self.variables[name] = value


class MemoryStack:
    def __init__(self, memory=None):
        self.stack = [memory or Memory("Global")]

    def get(self, name: str):
        for memory in reversed(self.stack):
            if memory.has_key(name):
                return memory.get(name)
        raise Exception(f"Variable {name} not found")

    def insert(self, name: str, value):
        self.stack[-1].put(name, value)

    def set(self, name: str, value):
        for memory in reversed(self.stack):
            if memory.has_key(name):
                memory.put(name, value)
                return
        self.insert(name, value)

    def push(self, memory):
        self.stack.append(memory)

    def pop(self):
        return self.stack.pop()


