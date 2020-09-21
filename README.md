
# FORWARD

In the process of experimenting with a basic reduction operation on frame data from OpenAI retro, I made this visualizer to make sure I wasn't running into any conceptual or implementation bugs.

It runs as a webserver and has basic control operations, as well as the ability to download created replay files such as video. It currently only supports NES games.

See a live version [here](http://ec2-54-176-62-21.us-west-1.compute.amazonaws.com).

## Use

    ./interface.sh

Docker is the main dependency. `interface.sh` builds a Docker image, which may take several minutes to run the first time, and instantiates a throwaway container in which it runs the server. The system expects roms in the base/roms folder.

Not yet complete. The idea is to be able to run a command such as `./interface.sh replay1 replay2 ...` and get a YouTube-like display of replays, such as those which have been generated by an ML agent.