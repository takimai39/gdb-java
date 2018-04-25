import sys
import gdb

class target(gdb.Command):
    "print target class and method name"
    def __init__(self):
        gdb.Command.__init__(self, 'target', gdb.COMMAND_NONE, gdb.COMPLETE_NONE)

    def invoke(self, arg, from_tty):

        # jvm_vers = gdb.execute("p JDK_Version::_runtime_version", False, True).split()[-1]
        # jvm_vers = jvm_vers[1:4]
        # print "%s" % jvm_vers

        ciMethod = arg.split()[-1]
        name         = gdb.execute("p ({ciMethod}" + ciMethod + ")->_name", False, True).split()[-1]
        symbol       = gdb.execute("p ({ciSymbol}" + name + ")->_symbol", False, True).split()[-1]
        method_name  = gdb.execute("x/s &({Symbol}" + symbol + ")->_body", False, True).split()[-1]
        method_name  = method_name.replace("\"", "")

        holder       = gdb.execute("p ({ciMethod}" + ciMethod + ")->_holder", False, True).split()[-1]
        name         = gdb.execute("p ({ciInstanceKlass}" + holder + ")->_name", False, True).split()[-1]
        symbol       = gdb.execute("p ({ciSymbol}" + name + ")->_symbol", False, True).split()[-1]
        class_name   = gdb.execute("x/s &({Symbol}" + symbol + ")->_body", False, True).split()[-1]
        class_name   = class_name.replace("\"", "")
        class_name   = class_name.replace("\\001", "")

        print "exclude %s %s" % (class_name, method_name)

target()


