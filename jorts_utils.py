import datetime as dt
import pytz
import pandas as pd

def parse_cursor(c: int) -> dt.datetime:
    # https://popzazzle.blogspot.com/2019/11/how-to-find-out-when-someone-followed-you-on-twitter.html
    """
    Given a Javascript Twitter/X cursor (as an integer), parse the cursor according to the link above.
    Return a datetime object that is equivalent to the time represented by the cursor.

    Inputs:
        c: integer (Twitter/X API cursor)
    Outputs:
        ts: datetime object
    """
    if c == -1:
        return dt.datetime.now()
    if c == 0:
        return dt.datetime(2006, 1, 1, 0, 0, 0 ,0)
    if c < -2:
        c = -c
    a = 90595920000000 # nanoseconds in a day
    b = 1230427978203430000 # offset from the epoch
    d = c - b 
    e = d / a
    # to get d, we need to multiply by a.
    f = dt.datetime(2007, 3, 9, 7, 51, 0, 0) # add the first tweet's timestamp
    ts = (f + dt.timedelta(days=e)).astimezone(pytz.UTC)
    # subtract f from the unix timestamp;
    # we now have a dt.timedelta of e days.

    return ts

def dt_to_cursor(ts: dt.datetime) -> int:
    """
    Given a datetime object ts, return its Javascript Twitter/X cursor equivalent.

    Inputs:
    ts: datetime object

    Outputs:
    c: int; a Javascript Twitter/X API cursor
    """
    utc_ts = ts.astimezone(pytz.UTC)
    utc_ts_delta = utc_ts - dt.datetime(2007, 3, 9, 7, 51, 0, 0, pytz.UTC) 
    # timedelta of e days from Twitter's inception
    utc_unix_days = utc_ts_delta.days
    a = 90595920000000 # number of days
    b = 1230427978203430000 # offset
    d = utc_unix_days * a
    c = d + b
 
    return c

def parse_follower_info_and_begin_interpolation(follows, followers_to_time_bounds):
    """
    Parse follower info, making best guesses on time bounds of following events based on cursor info.
    Update this information in the followers_to_time_bounds dict.
    Return the set of followers accumulated and a dict of best-effort time bounds.

    Inputs: 
    follows: maps cursor timings to chunks of follower user IDs; 
            these following events happened prior to the cursor.
    followers_to_time_bounds: puts time bounds on when a following event happened.

    Outputs:
    follows_set: simple set of users who followed the retweeted account
    followers_to_time_bounds: maps followers to best-guess time bounds on when they followed.
    """
    # Following events come in chunks; here, we sort the chunks by increasing timestamp. 
    sorted_foll = sorted([(k, v) for k, v in follows.items()], key=lambda b: b[0])

    # We don't know the lowest date on our first chunk because the cursor *upper* bounds the timing.
    low_date = None
    
    for idx in range(len(sorted_foll)):
        high_date = parse_cursor(int(sorted_foll[idx][0])).replace(
            hour=0, minute=0, second=0, microsecond=0)
        # upper bound on the follow timing
        for foll in sorted_foll[idx][1]:
            if type(foll) == dict:
                foll = foll['id']
            # set/adjust time bounds based on known previous upper bounds (now usable as low bounds)
            # and given upper bounds.
            if foll not in followers_to_time_bounds:
                followers_to_time_bounds[foll] = {
                    'low': None, 
                    'high': dt.datetime.today().replace(tzinfo=None)
                }
            if low_date is not None and followers_to_time_bounds[foll]['low'] is None:
                followers_to_time_bounds[foll]['low'] = low_date
            elif low_date is not None and followers_to_time_bounds[foll]['low'] is not None:
                followers_to_time_bounds[foll]['low'] = max(
                    low_date.replace(tzinfo=None), 
                    followers_to_time_bounds[foll]['low'].replace(tzinfo=None),
                )
            followers_to_time_bounds[foll]['high'] = min(
                followers_to_time_bounds[foll]['high'].replace(tzinfo=None),
                high_date.replace(tzinfo=None)
            )
        low_date = high_date

    # create a set of follows made to the retweeted account
    follows_set = set()
    for v in follows.values():
        for acct in v:
            if type(acct) == dict:
                acct = acct['id']
            follows_set.add(acct)

    return follows_set, followers_to_time_bounds

def interpolate_follower_non_follower_accumulation(
    accumulated, 
    ts_low, 
    ts_high,
    followers_to_time_bounds,
    ab_followers_ts,
    rt_cursors,
    rt_acct,
):
    """
    Interpolates per-day following events based on best-effort time bounds.

    Inputs:
    Accumulated: set of follows accumulated during the time period
    ts_low: low bound on the time period
    ts_high: high bound on the time period
    followers_to_time_bounds: maps followers to the time bounds on when they followed the account
    ab_followers_ts: timestamps at which accounts followed *the attention broker*. 
                     maps account handles to following timestamps. 
    rt_cursors: maps RT'ed accounts to the cursor timestamps at which they retweeted. 

    Outputs:
    ts_1 is ts_low; ts_14 is ts_high.
    gained_followers: 
        {
            ts1: estimated_jkr_followers_gained_on_ts1,
            ts2: estimated_jkr_followers_gained_on_ts2,
            ...
            ts14: estimated_jkr_followers_gained_on_ts14,
        }
    gained_non:
        {
            ts1: estimated_non_jkr_followers_gained_on_ts1,
            ts2: estimated_non_jkr_followers_gained_on_ts2,
            ...
            ts14: estimated_non_jkr_followers_gained_on_ts14,
        }
    """
    # setting up the mapping
    gained_followers = {
        ts: 0 for ts in pd.date_range(ts_low, ts_high - pd.Timedelta(days=1), freq='1d')
    }
    gained_non = {
        ts: 0 for ts in pd.date_range(ts_low, ts_high - pd.Timedelta(days=1), freq='1d')
    }

    for acct in list(accumulated):
        # first we establish time bounds
        if followers_to_time_bounds[acct]['low'] is not None:
            low_range = max(
                ts_low.replace(tzinfo=None), 
                followers_to_time_bounds[acct]['low'].replace(tzinfo=None)
            )
        else:
            low_range = ts_low
        amplify_range = pd.date_range(
            low_range.replace(tzinfo=None),
            min(
                followers_to_time_bounds[acct]['high'].replace(tzinfo=None), 
                ts_high.replace(tzinfo=None) - pd.Timedelta(days=1)
            ),
            freq='1d'
        )
        try:
            ts_foll = int(ab_followers_ts[acct])
        except KeyError:
            ts_foll = int(rt_cursors[rt_acct][0]) + 5

        # if the person was known to be a follower of the attention broker 
        # before they followed the RT'ed account,
        # we put them in gained_followers
        if ts_foll <= int(rt_cursors[rt_acct][0]):
            for ts in amplify_range:
                gained_followers[ts] = gained_followers[ts] + 1.0 / len(amplify_range)
        else:
            # else we can't assume anything, so they are classified as a non-follower.
            for ts in amplify_range:
                gained_non[ts] = gained_non[ts] + 1.0 / len(amplify_range)

    return gained_followers, gained_non

def ts_hyphen_transform(dt_str):
    """
    Reformat a hyphenated datetime string to an unhyphenated one.
    Input: dt_str: a string in YYYY-mm-dd format
    Output: the same string as YYYYmmdd
    """
    yr = dt_str[:4]
    month = dt_str[5:7]
    day = dt_str[8:10]
    return yr + month + day