class SingletonState:
    _instance = None  # holds the single instance

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            # init default state as off
            cls._instance.state = "off"
        return cls._instance

    def turn_on(self):
        self.state = "on"

    def turn_off(self):
        self.state = "off"

    def get_state(self):
        return self.state


# # class testing:
# singleton1 = SingletonState()
# singleton2 = SingletonState()

# print(singleton1.get_state())  # off
# singleton1.turn_on()
# print(singleton2.get_state())  # on, same instance
# singleton2.turn_off()
# print(singleton1.get_state())  # off
