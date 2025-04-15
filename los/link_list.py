

class ListNode:
    def __init__(self, val=None, next=None):
        self.val = val
        self.next = next


class LinkList:
    def __init__(self):
        self.head = None

    # 打印链表
    def print_list(self):
        current = self.head
        while current:
            print(current.val, end=" -> " if current.next else "\n")
            current = current.next

    # 在链表尾部添加节点
    def append(self, path_point):
        new_node = ListNode(path_point)
        if not self.head:
            self.head = new_node
            return
        last_node = self.head
        while last_node.next:
            last_node = last_node.next
        last_node.next = new_node

    # 在链表头 添加节点
    def prepend(self, path_point):
        new_node = ListNode(path_point)
        new_node.next = self.head
        self.head = new_node

    # 删除指定值的节点
    def delete_node(self, path_point):
        current = self.head
        if current and current.val == path_point:
            self.head = current.next
            return
        prev = None
        while current and current.val != path_point:
            prev = current
            current = current.next
        if current:
            prev.next = current.next

    # 清空链表
    def clear(self):
        self.head = None

        # 判断链表是否为空
    def is_empty(self):
        return self.head is None
