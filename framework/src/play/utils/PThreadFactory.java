package play.utils;

import java.util.concurrent.ThreadFactory;
import java.util.concurrent.atomic.AtomicInteger;

public class PThreadFactory implements ThreadFactory {

    final ThreadGroup group;
    final AtomicInteger threadNumber = new AtomicInteger(1);
    final String namePrefix;

    public PThreadFactory(String poolName) {
        //SecurityManager s = System.getSecurityManager(); // SecurityManager is deprecated and marked for removal.
        // group = (s != null) ? s.getThreadGroup() : Thread.currentThread().getThreadGroup(); // SecurityManager.getThreadGroup() by default, it returns the thread group of the current thread.
		group = Thread.currentThread().getThreadGroup();
		namePrefix = poolName + "-thread-";
    }

    @Override
    public Thread newThread(Runnable r) {
        Thread t = new Thread(group, r, namePrefix + threadNumber.getAndIncrement(), 0);
        if (t.isDaemon()) {
            t.setDaemon(false);
        }
        if (t.getPriority() != Thread.NORM_PRIORITY) {
            t.setPriority(Thread.NORM_PRIORITY);
        }
        return t;
    }
}
