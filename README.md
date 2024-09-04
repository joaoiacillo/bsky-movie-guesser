# Bsky Movie Guesser

BlueSky social media bot for guessing movies collectively and scoring points.

## Getting Started

WIP...

## How it Works

> This section describes the exact steps the bot performs in version 1.0.0.

Whenever a round starts, the bot picks a random movie and fetches exactly four
images of it. The images are randomly selected, so that whenever the same movie
gets picked in the future, the bot won't select the same pictures. It uses the
[TMDB API](https://developer.themoviedb.org/docs/getting-started) as the main
(and only) movie data source.

After that, each image go through the process of optimizing, censuring, and
then watermarking. These are the steps that happen in each one of them:

- Optimizing: Resizes the image to 1280x720, converts the image to JPEG for 
compressing the color palette and  setting its quality according to the env. 
var `TMDB_IMAGE_QUALITY`. This ensures that all images will be sent properly.
- Censuring: Hides the majority of the image, only letting a small window
visible so that the guess challenge increases.
- Watermarking: Inserts the TMDB watermark at the bottom of the image. This
properly attributes them as the source.

After all images go through that process, they are immediately sent to BlueSky
through their API. This lets people know that a new round has just started,
and  that they have 1 hour to guess correctly. The code sits idle during that
time.

After one hour, the bot grabs a _Record_ of the thread, and warns the users
that the guess time is over. It then goes through each reply that was sent. It
doesn't go further than the depth of `1`, so that users can talk and discuss
each other's comments. The process of comparing the attempts with the movie
title begins right after that.

For the comparison, the bot uses the
[_Levenshtein distance_](https://en.wikipedia.org/wiki/Levenshtein_distance)
for measuring the  similarity between the movie title and the attempt made by
the user. In fact,  it only does the comparison after "cleaning" both of the
strings, that is: removing extra spaces, symbols and converting to lower case.
This effectively  improves the comparison algorithm as fewer characters will
be computed, and  characters that are not letters, nor spaces nor numbers
won't affect the final  result.

> Comparing the strings byte by byte is a completely WRONG way of determining
> if a user has got the title right. Users commit typos when they write, or
> sometimes they just can't remember the full title. If one single byte is
> different from the movie title, the computer says that it's incorrect, when
> in fact we humans know that it's a false negative. Computers  don't think
> like us.

The comparison will result in a score between 0 and 100, which is the percent
of similarity. The env. var `BOT_THRESHOLD` holds a number that represents the
minimum value that the score needs to be considered a correct attempt. This
goes through each reply.

Comparisons made, the bot then calculates the percentage of correctness by
dividing the amount of correct attempts by the total amount of attempts. After
that, it posts the results and the time for the next round.

## Logging

By default, logging to files is used, ensuring that you can always retrieve
information from older runtimes and send clear and useful bug reports.

You can find all log files in `.logs`, located in the bot's root directory,
set by `consts.ROOT_DIR`, which is normally the folder that this README is
in. The files end with `.log` and provide the timestamp of when they were
created, so they will always be organized chronologically.

Printing to the console is turned off by default. But you can enable it and
disable logging to files by setting the environment variable `BOT_DEBUG_MODE`
to `'true'`. **Please keep in mind that we don't recommend using this mode in
production.**

This is how a log line might look like:

```log
2024-09-03 11:31:35,447:INFO:bsky.bot:main: Bsky client initialized as @bskymovieguesser.iacillo.dev.br
```

