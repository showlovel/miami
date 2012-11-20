
from miami import app, zeroing
from apscheduler.scheduler import Scheduler


def main():
    # Start the scheduler
    sched = Scheduler()
    sched.start()
    sched.add_cron_job(zeroing, hour='23')
    app.run()

if __name__ == "__main__":
    main()