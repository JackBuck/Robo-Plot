import queue
import threading
import time


class Job:
    def __init__(self):
        self.return_value = None
        self.print_output = []
        self.complete = False
        self.exception = None

    def do_work(self):
        try:
            self._do_work_core()
        finally:
            self.complete = True

    def _do_work_core(self):
        raise NotImplementedError('Clients must override this method to specify the work to be done.')


class PrintJob(Job):
    def __init__(self, wrapped_job: Job):
        super().__init__()
        self._inner_job = wrapped_job
        self._stop_printing = False

    def _do_work_core(self):
        while not self._inner_job.complete:
            time.sleep(0.1)

        if self._inner_job.print_output is not None:
            for line in self._inner_job.print_output:
                print(line)


class Worker(threading.Thread):
    def __init__(self, job_queue: queue.Queue, thread_name: str = None):
        self._job_queue = job_queue
        self._keep_working = True
        super().__init__(target=self._process_job_queue, name=thread_name)

    def _process_job_queue(self):
        while self._keep_working:
            job = self._job_queue.get()  # type: Job
            # We need to trigger the end of all jobs by processing a job from the queue because the get call is blocking
            if job is None:
                break
            job.do_work()
            self._job_queue.task_done()

    def make_this_the_last_job(self):
        self._keep_working = False


class JobProcessingStation:
    """A class to manage multiple worker threads around a queue and synchronise the console output."""

    def __init__(self, num_workers: int = 1, name: str = None):
        self._queue_lock = threading.Lock()
        self._job_queue = queue.Queue()
        self._print_queue = queue.Queue()

        self._main_workers = []
        for i in range(num_workers):
            worker_name = name + ': worker {}'.format(i) if name is not None else None
            worker = Worker(self._job_queue, thread_name=worker_name)
            self._main_workers.append(worker)
            worker.start()

        worker_name = name + ': print worker' if name is not None else None
        self._print_worker = Worker(self._print_queue, thread_name=worker_name)
        self._print_worker.start()

    def add_job(self, job: Job):
        if job is None:
            # Raise to avoid confusion with intentionally/unintentionally passing in None
            raise ValueError('Cannot add None as a job!')

        with self._queue_lock:
            self._job_queue.put(job)
            self._print_queue.put(PrintJob(job))

    def signal_no_more_jobs(self):
        with self._queue_lock:
            for _ in self._main_workers:
                self._job_queue.put(None)
            self._print_queue.put(None)

    def join(self):
        self._job_queue.join()
