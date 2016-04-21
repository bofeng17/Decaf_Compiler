class IR():
    def __init__(self, opcode, operandList, comment=""):
        self.opcode = opcode
        self.operandList = operandList
        self.comment = comment
    def __str__(self):
        return "{0} {1}#{2}\n".format(self.opcode, ', '.join(self.operandList),self.comment)


class Label():
    def __init__(self, label_name, comment=""):
        self.label_name = label_name
        self.comment = comment
    def __str__(self):
        return "{0}: #{1}\n".format(self.label_name, self.comment)

