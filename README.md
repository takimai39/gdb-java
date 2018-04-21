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
