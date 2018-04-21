# gdb-java
python script for debugging java core

# sp.py - print safepoint status
Java スレッドのステータスを表示します。
以下のように、Status: が synchronizing であれば JVM 自体は、スレッドダンプの出力や Full GC などを実行するために、全てのスレッドを safepoint と呼ばれる所まで処理を進めようとしています。
waiting to block が 1 ですので、このコアを取得した時点では 1 つのスレッドが、未だ safepoint まで到達できていない事を示しています。
続いて、個々の Java Thread のステータスをレポートしていますが、この場合　LWP 2409 が running 状態であり safepoint に達していません。

スレッドダンプも出力されない Java VM のハングアップの事象に関しては、このような状態になっているケースが多いと思われます。
sp.py として JavaThread の safepoint に関するステータスをレポートする簡単なスクリプトを作成して見ました。

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
