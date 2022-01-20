class Message:
    def __init__(self, message, header_size, message_size=None):
        """
        Ths function is used to initialize the message object.
        :param message: The message to be sent
        :type message: str
        :param header_size: The size of the header of the communication protocol
        :type header_size: int
        :param message_size: The size of the message to be sent. If not specified, the message size is assumed to be the size of the message. otherwise, the message size is assumed to be the specified size. It should be noted that specifiying the message size is optional, and it is used only to create a message and acummulate buffered data to it.
        :type message_size: int/None
        """
        if message_size is not None:
            self.message_size = message_size
            self.is_complete = False
        else:
            self.message_size = len(message)
            self.is_complete = True
        self.header_size = header_size
        self.message = f"{self.message_size: <{self.header_size}}" + message

    def get_plain_msg(self):
        """
        This function is used to get the plain message from the message object
        :return: The plain message
        :rtype: str
        """
        return self.message[self.header_size:]
    
    @classmethod
    def create_message_from_plain_data(cls, plain_data, header_size):
        """
        This function is used to create a message from the plain data.
        :param plain_data: The plain data to be sent
        :type plain_data: str
        :param header_size: The size of the header of the communication protocol
        :type header_size: int
        """
        msg = plain_data[header_size:]
        if int(plain_data[:plain_data.find(" ")]) == len(msg):
            return cls(msg, header_size)
        return cls(msg, header_size, int(plain_data[:plain_data.find(" ")]))

    def __iadd__(self, string):
        """
        This function is used to accumulate the message ON RECIEVEING ONLY
        :param string: The string to be added to the message
        :type string: str
        """
        if self.is_complete:
            raise ValueError("The message is already complete")
        self.message += string
        self.is_complete = len(self.get_plain_msg()) == self.message_size
        return self

    def __str__(self):
        """
        This function is used to return the header + message
        :return: The header + message
        :rtype: str
        """
        return self.message


def main():
    m = Message("Hello", 20, 11)
    print(m)
    print(m.is_complete)
    m += "World!"
    print(m)
    print(m.is_complete)
    m += "!"

    # m = Message.create_message_from_plain_data("15      Hello World!", 8)
    # print(m)
    # print(m.is_complete)
    # m += "123"
    # print(m)
    # print(m.is_complete)
    # m += "456"

if __name__ == "__main__":
    main()
