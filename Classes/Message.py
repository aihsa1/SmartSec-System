class Message:
    def __init__(self, message, header_size, message_size=None):
        """
        Ths function is used to initialize the message object.
        :param message: The message to be sent
        :type message: str/bytesr
        :param header_size: The size of the header of the communication protocol
        :type header_size: int
        :param message_size: The size of the message to be sent. If not specified, the message size is assumed to be the size of the message. otherwise, the message size is assumed to be the specified size. It should be noted that specifiying the message size is optional, and it is used only to create a message and acummulate buffered data to it.
        :type message_size: int/None
        """
        # set is_compelete and message_size according to the params
        if message_size is not None:
            self.message_size = message_size
            self.is_complete = False
        else:
            self.message_size = len(message)
            self.is_complete = True

        self.header_size = header_size
        
        # set is_compelete and message_size according to the message dtype
        if isinstance(message, bytes):
            self.message = f"{self.message_size: <{self.header_size}}".encode(
            ) + message
        else:
            self.message = f"{self.message_size: <{self.header_size}}" + message

    def get_plain_msg(self):
        """
        This function is used to get the plain message from the message object
        :return: The plain message
        :rtype: str
        """
        return self.message[self.header_size:]  # takes str and bytes into account

    @classmethod
    def create_message_from_plain_data(cls, plain_data, header_size):
        """
        This function is used to create a message from the plain data.
        :param plain_data: The plain data to be sent
        :type plain_data: str
        :param header_size: The size of the header of the communication protocol
        :type header_size: int
        :return: The message object
        :rtype: Message
        """
        space = b" " if isinstance(plain_data, bytes) else " "
        msg = plain_data[header_size:]
        if int(plain_data[:plain_data.find(space)]) == len(msg):
            return cls(msg, header_size)
        return cls(msg, header_size, int(plain_data[:plain_data.find(space)]))

    def __iadd__(self, string):
        """
        This function is used to accumulate the message ON RECIEVEING ONLY
        :param string: The string to be added to the message
        :type string: str/bytes
        :return: The message object with the added data
        :rtype: Message
        """
        if self.is_complete:
            raise ValueError("The message is already complete")
        if not((isinstance(string, str) and isinstance(self.message, str)) or (isinstance(string, bytes) and isinstance(self.message, bytes))):
            raise TypeError(
                "The message and the string must be of the same type")
        if len(string) + len(self.message[self.header_size:]) > self.message_size:
            raise ValueError(
                f"the given string is too long. It should be at most {self.message_size - len(self.message[self.header_size:])}, and you gave {len(string)}")

        self.message += string
        self.is_complete = len(self.get_plain_msg()) == self.message_size
        return self

    def splitted_data_generator(self, batch_size):
        """
        This function is used to generate the splitted data indicies from the message
        :param batch_size: The size of the batch
        :type batch_size: int
        :return: yields the splitted data indicies
        :rtype: generator
        """
        for i in range(len(self.message) // batch_size):
            start_index = i*batch_size
            yield [start_index, start_index + batch_size]
        yield [(i + 1) * batch_size, (start_index + batch_size) + len(self.message) % batch_size]

    def __str__(self):
        """
        This function is used to return the header + message
        :return: The header + message
        :rtype: str
        """
        return self.message.__str__()  # takes str and bytes into account


def main():
    # m = Message("Hello", 20, 11)
    # print(m)
    # print(m.is_complete)
    # m += "World!"
    # print(m)
    # print(m.is_complete)
    # m += "!"

    # m = Message.create_message_from_plain_data("15      Hello World!", 8)
    # print(m)
    # print(m.is_complete)
    # m += "123"
    # print(m)
    # print(m.is_complete)
    # m += "456"

    # m = Message("123".encode(), 8, 6)
    # print(m.get_plain_msg())
    # m += "456".encode()
    # print(m.get_plain_msg())
    # print(m.message_size)
    # print(m)

    m = Message.create_message_from_plain_data(b"289         0 1", 12)
    print(m)

    # m = Message(" ".join([str(i) for i in range(100)]), 12)
    # print(m)
    # print(len(m.message))
    # print(list(m.splitted_data_generator(11)))


if __name__ == "__main__":
    main()
