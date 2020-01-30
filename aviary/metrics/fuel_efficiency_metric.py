"""
Basic fuel efficiency metric. Specification is:

Given initial, target and current altitudes (or flight levels),
at every time step, return (*see note below):

-1 * |max{targ_alt, init_alt} - curr_alt|/|targ_alt - init_alt|

Explanation:

This metric is equivalent to the following two-part specification.

I) If init_alt <= targ_alt, return:

-1 * |targ_alt - curr_alt|/(targ_alt - init_alt)

This rewards time spent close to the target altitude and penalises time spent away (above or below),
so incentivises the "climb as soon as possible" rule. The penalty is proportional to the current
vertical separation from the target, normalised relative to the initial separation.

II) If init_alt > targ_alt, return:

-1 * |init_alt - curr_alt|/(init_alt - targ_alt)

This is the same as the preceding case except the roles of init_alt and targ_alt are reversed
on the grounds that, when the plane is requesting to descend, time spent away from the initial
altitude is less fuel efficient. When this metric is considered in combination with the sector
exit metric, their relative scales must be chosen so that the benefit of exiting at the target
altitude outweighs the penalty for deviating from the initial (more fuel efficient) altitude.
In that case, the optimal trajectory will be one that remains at the initial altitude as long
as possible, but descends in time to hit the exit target.

(*) NB: to make it easier to combine metrics sensibly, we actually want to bound them
in the range [-1, 0], so the correct formula is:

-1 * min{|max{targ_alt, init_alt} - curr_alt|/|targ_alt - init_alt|, 1}

"""
# author: Tim Hobson
# email: thobson@turing.ac.uk

def fuel_efficiency_metric(current_flight_level, requested_flight_level, initial_flight_level):
    """
    Computes the fuel efficiency metric for the current timestep.

    :param current_flight_level: The current flight level or altitude
    :param requested_flight_level: The requested flight level or altitude
    :param initial_flight_level: The initial flight level or altitude
    :return: A float. The score for the current timestep according to the fuel efficiency metric.
    """

    num = abs(max(requested_flight_level, initial_flight_level) - current_flight_level)
    denom = abs(requested_flight_level - initial_flight_level)
    if denom == 0:
        return 0
    return -1 * min(1, num/denom)
