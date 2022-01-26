import multiprocessing, time


def get_input(pipe_socket: multiprocessing.Pipe):
    time.sleep(10)
    pipe_socket.send(r"C:\Users\USER\Desktop\Cyber\PRJ\img107.jpg")

def save_img(pipe_socket: multiprocessing.Pipe):
    path = pipe_socket.recv()
    print(path)


def main():
    x, y = multiprocessing.Pipe()
    processes = [
        multiprocessing.Process(name="input process", target=get_input, args=(x,)),
        multiprocessing.Process(name="save process", target=save_img, args=(y,))
    ]
    for p in processes:
        p.start()
    for p in processes:
        p.join()
    print("Done")

if __name__ == '__main__':
    main()