import sys
import gdb

class safepoint(gdb.Command):
    "print safepoint status"
    def __init__(self):
        gdb.Command.__init__(self, 'safepoint', gdb.COMMAND_NONE, gdb.COMPLETE_NONE)

    def invoke(self, arg, from_tty):

        print "--------------------------------------------------------------------"
        print "Status:\t\t\t" + gdb.execute("p SafepointSynchronize::_state", False, True).split()[-1]
        print "waiting to block:\t" + gdb.execute("p SafepointSynchronize::_waiting_to_block", False, True).split()[-1]
        print "LWP\tJava Thread Name\tStatus"
        print "--------------------------------------------------------------------"

        threadlist = gdb.parse_and_eval("Threads::_thread_list")
        while (str(threadlist) != "0x0"):
            safepoint_state = gdb.execute("p ((JavaThread *)" + str(threadlist) + ")->_safepoint_state", False, True ).split()[-1]
            state           = gdb.execute("p ((ThreadSafepointState *)" + str(safepoint_state) + ")->_type", False, True ).split()[-1]
            osthread        = gdb.execute("p ((JavaThread *)" + str(threadlist) + ")->_osthread", False, True ).split()[-1]
            threadObj       = gdb.execute("p ((JavaThread *)" + str(threadlist) + ")->_threadObj", False, True ).split()[-1]
            metadata        = gdb.execute("p &((Thread *)" + str(threadObj) + ")->_metadata_handles", False, True ).split()[-1]
            thread_id       = gdb.execute("p ((OSThread *)" + str(osthread) + ")->_thread_id", False, True ).split()[-1]
            pthread_id      = gdb.execute("p ((OSThread *)" + str(osthread) + ")->_pthread_id", False, True ).split()[-1]

            thread_name = ""
            for i in range(80):
                pos = long(metadata, 16) + i * 2
                ch =  int(gdb.execute("x/bx " + str(pos), False, True).split()[-1], 16)
                if 0x20 > ch or 0x7e < ch:
                    break
                ch = ("%c" % ch)
                thread_name = thread_name + ch

            print ("LWP %s %-20s	 %s" % (thread_id, thread_name, state))
            threadlist      = gdb.execute("p ((JavaThread *)" + str(threadlist) + ")->_next", False, True ).split()[-1]

safepoint()


