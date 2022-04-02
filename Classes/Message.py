from typing import Union, Generator, List
from CommunicationCode import CommunicationCode


class Message:
    DEFAULT_HEADER_SIZE = 20

    def __init__(self, message: Union[str, bytes], header_size: int=DEFAULT_HEADER_SIZE, message_size: Union[int, None]=None, code: CommunicationCode=CommunicationCode.VIDEO) -> None:
        """
        Ths function is used to initialize the message object.
        :param message: The message to be sent
        :type message: Union[str, bytes]
        :param header_size: The size of the header of the communication protocol
        :type header_size: int
        :param message_size: The size of the message to be sent. If not specified, the message param size is assumed to be the size of the message. otherwise, the message size is assumed to be the specified size. It should be noted that specifiying the message size is optional, and it is used only to create a message and acummulate buffered data to it.
        :type message_size: Union[int, None]
        """
        # set is_compelete and message_size according to the params
        if message_size is not None:
            self.message_size = message_size
            self.is_complete = False
        else:
            self.message_size = len(message)
            self.is_complete = True

        self.code = code
        self.header_size = header_size

        # set is_compelete and message_size according to the message dtype
        if isinstance(message, bytes):
            self.message = f"{(str(self.message_size) + '_' + self.code): <{self.header_size}}".encode(
            ) + message
            self.code = self.code.encode()
        else:
            self.message = f"{(str(self.message_size) + '_' + self.code): <{self.header_size}}" + message

    def get_plain_msg(self):
        """
        This function is used to get the plain message from the message object
        :return: The plain message
        :rtype: str
        """
        return self.message[self.header_size:]  # takes str and bytes into account

    @classmethod
    def create_message_from_plain_data(cls, plain_data: bytes, header_size: int=DEFAULT_HEADER_SIZE) -> 'Message':
        """
        This function is used to create a message from the plain data.
        :param plain_data: The plain data to be sent
        :type plain_data: str
        :param header_size: The size of the header of the communication protocol
        :type header_size: int
        :return: The message object if the plain data is not empty, otherwise, None
        :rtype: Message
        """
        underscore = "_"
        
        if isinstance(plain_data, bytes):
            underscore = underscore.encode()
            underscore_index = plain_data.find(underscore)
            code = plain_data[underscore_index + 1: underscore_index + 2]
        else:
            underscore_index = plain_data.find(underscore)
            code = plain_data[underscore_index + 1: underscore_index + 2].encode()

        msg = plain_data[header_size:]
        complete_len = int(plain_data[:plain_data.find(underscore)])
        
        if len(msg) == 0 or complete_len == len(msg):
            return cls(msg, header_size, code=code.decode())
        return cls(msg, header_size, complete_len, code=code.decode())

    def __iadd__(self, string: Union[str, bytes]) -> 'Message':
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

    def splitted_data_generator(self, batch_size: int) -> Generator[List[int], None, None]:
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
        yield [len(self.message) // batch_size * batch_size, len(self.message) // batch_size * batch_size + len(self.message) % batch_size]

    def __str__(self) -> str:
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

    # m = Message.create_message_from_plain_data(b"5         01", 12)
    # print(m)
    # m += "123"
    # print(m)
    # m += "123"

    # m = Message(" ".join([str(i) for i in range(15)]), 12)
    # print(m)
    # print(len(m.message))
    # print(list(m.splitted_data_generator(11)))

    # m = Message(b"hello world!", message_size=30)
    # print(m)
    # print(m.code)
    # m += b"hi"
    # m += b"hi"
    # m += b"hi"
    # m += b"hi"
    # print(m)
    # print(m.code)

    # m = Message.create_message_from_plain_data(
    #     "12_1                Hello World!", 20)
    # print(m.message)
    # print(m.message_size)
    # print(m.is_complete)
    # print(m.code)
    # print(type(m.code))
    from AESEncryption import AESEncryption
    e1 = AESEncryption()
    e2 = AESEncryption(key=e1.key)
    print(e1.key)
    print(e2.key)
    content = b"hi"
    content_enc = e1.encrypt(content)
    m = Message(content_enc)
    print(m)
    print(len(m.message))
    
    


if __name__ == "__main__":
    main()
