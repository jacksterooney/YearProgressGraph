import tweepy
import re
import json
import matplotlib.pyplot as plt
import numpy as np

# Tweepy authentication setup
consumer_key = <consumer key here>
consumer_secret = <consumer secret here>

access_token = <access token>
access_token_secret = <secret access token>

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)

api = tweepy.API(auth)

# Get the year progress user object
user = api.get_user('year_progress')

# Manually inputted tweet ids to split them into year sections
year_id_dict = {
    2018: (947618376704282624, 1079889947413368834),
    2017: (815346806267768832, 947618374288400384),
    2016: (682712850461097984, 815346803558285312)
}


def main():

    # Gather lists of (percentage, fav_count) for each year
    stats_2016 = get_stats(2016)
    stats_2017 = get_stats(2017)
    stats_2018 = get_stats(2018)

    # Average favorite count for each percentage point
    averages = average_stats(stats_2016, stats_2017, stats_2018)

    # Change data to two lists readable by matplotlib
    percentages = []
    fav_counts = []
    for pair in averages:
        percentages.append(pair[0])
        fav_counts.append(pair[1])

    # Remove frame lines and set size
    plt.figure(figsize=(12, 9))
    ax = plt.subplot(111)
    ax.spines["top"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["right"].set_visible(False)

    # Set ticks
    plt.xticks(np.arange(0, 101, 5))
    plt.xticks(fontsize=14)
    plt.yticks(fontsize=14)

    # Set labels
    plt.ylabel("Average Favourite Count", fontsize=16)
    plt.xlabel("Percentage Through Year (%)", fontsize=16)
    plt.title("Favourite count for tweets by @year_progress, averaged over 2016, 2017, and 2018", fontsize=16)

    # Ensure that the axis ticks only show up on the bottom and left of the plot.
    ax.get_xaxis().tick_bottom()
    ax.get_yaxis().tick_left()

    plt.xlim(0, 101)

    # Provide tick lines across the plot to help your viewers trace along
    # the axis ticks. Make sure that the lines are light and small so they
    # don't obscure the primary data lines.
    for y in range(5000, 20001, 5000):
        plt.plot(range(0, 101), [y] * len(range(0, 101)), "--", lw=0.5, color="black", alpha=0.3)

        # Remove the tick marks; they are unnecessary with the tick lines we just plotted.
    plt.tick_params(axis="both", which="both", bottom="off", top="off",
                    labelbottom="on", left="off", right="off", labelleft="on")

    # Plot graph
    plt.plot(percentages, fav_counts, color="#3F5D7D")

    plt.savefig("year_progress_fav_count.png", bbox_inches="tight")
    plt.show()


def get_stats(year):
    stats = []

    # Get initial and final tweet id for each year
    since_id = year_id_dict[year][0]
    max_id = year_id_dict[year][1]

    # Fetch timeline of all tweets between ids
    for tweet in api.user_timeline(screen_name='year_progress', count=200, include_rts=False,
                                   since_id=since_id, max_id=max_id):

        # Filter tweets by not being a reply and starting with a progress bar
        valid_tweet = tweet.text.startswith("\N{dark shade}") or tweet.text.startswith("\N{light shade}")
        if valid_tweet & (tweet.in_reply_to_status_id_str is None):

            # Load json
            jsons = json.loads(json.dumps(tweet._json))

            # Gather text and fav count
            text = (jsons["text"])
            fav_count = (jsons["favorite_count"])

            # Parse percentage point and fav count
            numbers = re.findall('\d+', text)
            percentage = map(int, numbers).__next__()

            stats.append((percentage, fav_count))

    return stats


def average_stats(stats_2016, stats_2017, stats_2018):
    averaged_stats = []
    for i in range(100):
        averaged_fav_count = ((stats_2016[i])[1] + (stats_2017[i])[1] + (stats_2018[i])[1]) / 3
        averaged_stats.append((100 - i, averaged_fav_count))
    return averaged_stats


if __name__ == '__main__':
    main()
