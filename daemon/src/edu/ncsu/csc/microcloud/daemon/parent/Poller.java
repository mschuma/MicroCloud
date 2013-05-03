package edu.ncsu.csc.microcloud.daemon.parent;

import java.util.List;
import java.util.concurrent.Executor;
import java.util.concurrent.LinkedBlockingQueue;
import java.util.concurrent.ThreadPoolExecutor;
import java.util.concurrent.TimeUnit;
import java.util.concurrent.locks.Condition;
import java.util.concurrent.locks.Lock;
import java.util.concurrent.locks.ReentrantLock;

public class Poller implements Runnable {
	private long pollingPeriod;
	private int childPort;
	private Executor executor;
	private final int IDLE_THREAD_PERIOD = 5;
	private final Lock lock;
	private final Condition executionsFinished;

	public Poller(long pollingPeriod, int childPort, int pollingThreads) {
		lock = new ReentrantLock();
		executionsFinished = lock.newCondition();
		executor = new ThreadPoolExecutor(pollingThreads, pollingThreads,
				IDLE_THREAD_PERIOD, TimeUnit.SECONDS,
				new LinkedBlockingQueue<Runnable>());
		this.pollingPeriod = pollingPeriod;
		this.childPort = childPort;
	}

	public void run() {
		long sleepingPeriod = pollingPeriod;
		while (true) {
			try {
				Thread.sleep(sleepingPeriod);
			} catch (Exception ex) {
				System.err.println("Error caught while sleeping in Poller");
				ex.printStackTrace();
			}

			try {
				lock.lock();
				long startTime = System.currentTimeMillis();
				executeChildren();
				executeFinishedRun();
				executionsFinished.await();
				long finishTime = System.currentTimeMillis();
				long elapsedTime = finishTime - startTime;
				sleepingPeriod = pollingPeriod - elapsedTime;
				System.out.println("Polling cycle took (ms)::" + elapsedTime);
				if (elapsedTime > pollingPeriod) {
					System.err
							.println("WARNING! Polling cycle took longer than specified, children may start to think parent is missing");
				}
			} catch (Exception ex) {
				System.err.println("Error caught executing children in Poller");
				ex.printStackTrace();
			} finally {
				lock.unlock();
			}

		}
	}

	private void executeFinishedRun() {
		executor.execute(new Runnable() {
			@Override
			public void run() {
				try {
					lock.lock();
					executionsFinished.signal();
				} catch (Exception ex) {
					System.err
							.println("Error caught while signalling in Poller");
					ex.printStackTrace();
				} finally {
					lock.unlock();
				}

			}
		});
	}

	private void executeChildren() {
		List<String> children = ParentDaemon.getChildren();
		if (children != null && children.size() > 0) {
			for (String child : children) {
				executor.execute(new ChildHealthCheck(child, childPort));
			}
		}
	}
}
