import time


def the_time_keeper(t=0.0, float_out=False):
    """
    This function provides the duration of a given task when called twice, once to initiate before task begins, and
    again, after task has completed, to return duration of task.

    Example usage is as follows:

        start_time = the_time_keeper()      # init with no value passed to t; time script begins
        # do stuff
        the_time_keeper(start_time)         # pass value to t; print duration of task

    Returned value is returned as follows:

        if t==0.0                           float value of the current time
        if t!=0.0 and float_out=True        task duration as float in seconds
        if t!=0.0 and float_out=False       task duration as formatted str

    :param t:                   float, optional     time previously returned by the Time Keeper
    :param float_out:           str, optional       if True, returns seconds as float; if False, returns as string
    :return:                    float or str        duration as seconds or formatted string
    """

    if t == 0.0:
        return time.time()
    else:
        tk = time.time() - t
        if float_out:
            return round(tk, 2)
        else:
            if tk < 60:
                tk = 'Duration: ' + str(round(tk, 2)) + ' seconds.'
            elif 60 < tk < 3600:
                tk = 'Duration: ' + str(round(tk / 60, 2)) + ' minutes.'
            else:
                tk = 'Duration: ' + str(round(tk / 60 / 60, 2)) + ' hours.'
            return tk
