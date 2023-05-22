import queue

q = queue.Queue()

q.put("1")
q.put("2")
print(q.get())
print(q.get())