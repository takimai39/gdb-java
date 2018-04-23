# gdb-java
python script for debugging java core

# sp.py - print safepoint status
個々の Java スレッドに関して safepoint のステータスを表示します。

Java VM がハングアップした時の core ファイルを以下のように確認してみます。このハング状態の場合 SIGQUIT を送ってもスレッドダンプも出力されません。
Status: が synchronizing であれば、JVM 自体はスレッドダンプの出力か、もしくは Full GC などを実行するため全てのスレッドを safepoint と呼ばれる所まで処理を進めようとしています。
waiting to block が 1 ですので、このコアを取得した時点では 1 つのスレッドが、safepoint まで到達できていません。
続いて、個々の Java Thread のステータスをレポートしていますが、この中では LWP 2409 が running 状態であり safepoint に達していません。
つまり LWP 2409 のスレッドが、Java VM のハングアップの原因です。

スレッドダンプも出力されない Java VM のハングアップの事象に関しては、このような状態になっているケースが多いと思われます。


```
$ gdb /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/bin/java ./core.2397
...中略 ...
(gdb) source sp.py
(gdb) safepoint
--------------------------------------------------------------------
Status:                 SafepointSynchronize::_synchronizing
waiting to block:       1
LWP     Java Thread Name        Status
--------------------------------------------------------------------
LWP 2398 DestroyJavaVM           ThreadSafepointState::_at_safepoint
LWP 2410 Timer                   ThreadSafepointState::_at_safepoint
LWP 2409 Worker                  ThreadSafepointState::_running
LWP 2407 Service Thread          ThreadSafepointState::_at_safepoint
LWP 2406 C1 CompilerThread1      ThreadSafepointState::_at_safepoint
LWP 2405 C2 CompilerThread0      ThreadSafepointState::_at_safepoint
LWP 2404 Signal Dispatcher       ThreadSafepointState::_at_safepoint
LWP 2403 ?                       ThreadSafepointState::_at_safepoint
LWP 2402 Reference Handler       ThreadSafepointState::_at_safepoint
(gdb)
```

# target.py
HotSpotコンパイラが原因でクラッシュした時に、以下のように実行して C2Compiler::compile_method の引数 target から、HotSpot 対象のクラス名とメソッド名を表示します。
出力された exclude class/name method を、Java VM を起動するディレクトリの .hotspot_compiler ファイルに記載することで次回から事象を回避できます。

```
# gdb /usr/lib/jvm/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/bin/java /usr/share/tomcat/core.22074
...
(gdb) bt
#0  0x00007fbc8b30f1f7 in raise () from /lib64/libc.so.6
#1  0x00007fbc8b3108e8 in abort () from /lib64/libc.so.6
#2  0x00007fbc8abc8eb9 in os::abort (dump_core=<optimized out>) at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/os/linux/vm/os_linux.cpp:1513
#3  0x00007fbc8adc7c46 in VMError::report_and_die (this=this@entry=0x7fbc72053810)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/share/vm/utilities/vmError.cpp:1060
#4  0x00007fbc8abd2b17 in JVM_handle_linux_signal (sig=11, info=0x7fbc72053ab0, ucVoid=0x7fbc72053980, abort_if_unrecognized=<optimized out>)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/os_cpu/linux_x86/vm/os_linux_x86.cpp:556
#5  0x00007fbc8abc62d8 in signalHandler (sig=11, info=0x7fbc72053ab0, uc=0x7fbc72053980)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/os/linux/vm/os_linux.cpp:4440
#6  <signal handler called>
#7  C2Compiler::compile_method (this=0x7fbc840a76b0, env=0x7fbc72054b00, target=0x7fbc4840ef40, entry_bci=-1)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/share/vm/opto/c2compiler.cpp:116
#8  0x00007fbc8a7c29c6 in CompileBroker::invoke_compiler_on_method (task=task@entry=0x7fbc8431cc40)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/share/vm/compiler/compileBroker.cpp:1993
#9  0x00007fbc8a7c391a in CompileBroker::compiler_thread_loop ()
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/share/vm/compiler/compileBroker.cpp:1815
#10 0x00007fbc8ad70c72 in JavaThread::thread_main_inner (this=0x7fbc840bb000)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/share/vm/runtime/thread.cpp:1710
#11 0x00007fbc8abc7e12 in java_start (thread=0x7fbc840bb000) at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/os/linux/vm/os_linux.cpp:790
#12 0x00007fbc8bccde25 in start_thread () from /lib64/libpthread.so.0
#13 0x00007fbc8b3d234d in clone () from /lib64/libc.so.6
(gdb) frame 7
#7  C2Compiler::compile_method (this=0x7fbc840a76b0, env=0x7fbc72054b00, target=0x7fbc4840ef40, entry_bci=-1)
    at /usr/src/debug/java-1.8.0-openjdk-1.8.0.131-11.b12.el7.x86_64/openjdk/hotspot/src/share/vm/opto/c2compiler.cpp:116
116       while (!env->failing()) {
(gdb) source target.py
(gdb) target 0x7fbc4840ef40
exclude org/apache/coyote/http11/AbstractInputBuffer addActiveFilter
(gdb) 
```
