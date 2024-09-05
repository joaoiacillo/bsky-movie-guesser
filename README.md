# Bsky Movie Guesser

BlueSky social media bot for guessing movies collectively and scoring points.

## Installing with Docker

We all love Docker, so we've provided a `Dockerfile` ready for building in
the root folder of this repository. It already uses the required Python
version, it's isolated and easy to manage. Use the following commands to
install with Docker:

### Configure the Environment Variables

There are required environment variables that need to be defined before
running. You can create the `.env` file according to
[Configuring the environment](#configuring-the-environment) since it will be
copied to the Docker image during building, or set them manually during the
`run` command.

### Building and Running

```bash
$ sudo docker build -t bsky-movie-guesser .
$ sudo docker run -it --rm --name bmg bsky-movie-guesser
````

## Installing Manually

The bot was created to be easy to configure and run. The only things to do are
install all requirements from pip, grab your credentials for the APIs and
configure the `.env` file. Let's go through those step-by-step.

### Install the requirements

> Keep in mind that the bot only works in **Python 3.9** or greater. You
> might get _type errors_ if using lower versions. It's also beneficial
> creating a virtual environment before installing the requirements.

Let's start with the easiest one. We assume that you have Python and pip
installed in your system. There is a `requirements.txt` file ready for you
in this repository root folder, just pull up your terminal and use
the command:

```bash
$ pip3 install -r requirements.txt
```

And that should do the job.

### Grab your credentials

You'll need to grab three credentials: one from TMDB, and two from BlueSky.

#### The Movie Database (TMDB)

TMDB is a free movie data source that allows you to use their API freely, as
long as you credit them. This bot already does that by watermarking each
image, so you won't need to worry about it.

Start heading to their [official website](https://www.themoviedb.org) and
signing-up. After that go into your **account** (not profile) settings and
switch to the **"API"** category. From there, generate your unique key. You
may see that it generates two keys: the API Key, and the API Read Access
Token. Grab the **access token**, that's the one we need.

#### BlueSky

For BlueSky, all you need is the **user handle** and an **App Password**.

> **PLEASE**, do NOT use your account password. Even though it's possible to
> use it, it's highly insecure. If you get your password leaked, other
> people will be able to access your account easily. App Passwords are meant
> to be used by bots and _limit what they can do with your account_.

App Passwords are created manually. Sign in to your account and head to
**Settings -> Advanced -> App Passwords**. Click on **"Add App Password"**
and give it a unique name. Do **NOT** check the box for allowing access to
the direct messages, the bot doesn't do that (yet). Proceed by clicking on
the big blue button **"Create App Password"**.

Copy the password it displays to you and paste it somewhere else. After
closing that dialog, the password will disappear and there's no way to
recover it. If you didn't copy it, you'll need create another one.

> We recommend creating two App Passwords: one for development, and one for
> production. Even though both allow access to the same account, if your
> development password gets leaked, your production password will be safe,
> and all you need to do is regenerate a new development one.

### Configuring the environment

There is a `.env.example` file located in the root folder of this repo. In
there you'll be able to find all environment variables and a comprehensive
description right along with other details.

Some of the environment variables are already defined for you due to their
default values, but some of them are marked as `[REQUIRED]`, and those need
to be filled with the right information, otherwise _the bot won't work at
all_.

Copy, or rename, the example file to `.env` and open it for editing. Change
the following variables to the credentials you grabbed before:

- `TMDB_API_ACCESS_TOKEN`
- `BSKY_HANDLE`
- `BSKY_PASSWORD`

You can then further explore the other environment variables, or proceed to
run the bot.

### Running the bot

Run the bot by calling the `main.py` file with Python 3:

```bash
$ python3 main.py
```

And that's it. Wait for the bot to boot up, and the game already starts. You
may notice that there is no visual indicator that it started running. That's
because printing to the console is disabled by defau lt. You can read more
about this and how to enable console printing in the
[Logging section](#logging).

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
  compressing the color palette and setting its quality according to the env.
  var `TMDB_IMAGE_QUALITY`. This ensures that all images will be sent properly.
- Censuring: Hides the majority of the image, only letting a small window
  visible so that the guess challenge increases.
- Watermarking: Inserts the TMDB watermark at the bottom of the image. This
  properly attributes them as the source.

After all images go through that process, they are immediately sent to BlueSky
through their API. This lets people know that a new round has just started,
and that they have 1 hour to guess correctly. The code sits idle during that
time.

After one hour, the bot grabs a _Record_ of the thread, and warns the users
that the guess time is over. It then goes through each reply that was sent. It
doesn't go further than the depth of `1`, so that users can talk and discuss
each other's comments. The process of comparing the attempts with the movie
title begins right after that.

For the comparison, the bot uses the
[_Levenshtein distance_](https://en.wikipedia.org/wiki/Levenshtein_distance)
for measuring the similarity between the movie title and the attempt made by
the user. In fact, it only does the comparison after "cleaning" both of the
strings, that is: removing extra spaces, symbols and converting to lower case.
This effectively improves the comparison algorithm as fewer characters will
be computed, and characters that are not letters, nor spaces nor numbers
won't affect the final result.

> Comparing the strings byte by byte is a completely WRONG way of determining
> if a user has got the title right. Users commit typos when they write, or
> sometimes they just can't remember the full title. If one single byte is
> different from the movie title, the computer says that it's incorrect, when
> in fact we humans know that it's a false negative. Computers don't think
> like us.

The comparison will result in a score between 0 and 100, which is the percent
of similarity. The env. var `BOT_THRESHOLD` holds a number that represents the
minimum value that the score needs to be considered a correct attempt. This
goes through each reply.

Comparisons made, the bot then calculates the percentage of correctness by
dividing the amount of correct attempts by the total amount of attempts. After
that, it posts the results and the time for the next round.

## Contributing

The door is always open for contributions! Send a pull request with the
modification, inclusion or discard that you made. You can also fork this
repository and work on another version, but always remember that this code
is under the [GPLv3 license](LICENSE).

## License

[GNU General Public License v3.0](LICENSE)
