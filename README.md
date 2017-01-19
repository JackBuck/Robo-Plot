# Robo-Plot
The main repository for our 2017 hackspace project.

## Project Structure
There are three top level folders:
  - `roboplot` - the top level python package,
  - `scripts` - contains scripts which exercise the `roboplot` package.,
  - `resources` - contains files (e.g. images) which can be used as input to scripts, or for test data, or anything else.

## Deploying to the pi
So as to be platform agnostic, deployment to the pi has been set-up to use git push via ssh.

To push your current branch of *Robo-Plot* to the pi, first make sure that you can `ping robo-plot`.
This will check that resolution of the hostname `robo-plot` is set up correctly.
On the Hacknet network, the pi broadcasts its name as `robo-plot` and the router magically maps `robo-plot` to the pi's ip address for us.
At my (Jack's) home, when using an ethernet connection, it was necessary to
  - tell the router to reserve an ip address for the pi
  - add this ip address to by `/etc/hosts` file.

Then add the pi's version of `Robo-Plot` as a git remote (setup to use `ssh`):
    git remote add robo-plot ssh://pi@robo-plot/~/SoftwareDevelopment/Robo-Plot

When you call
    git push robo-plot
you will be prompted for the login password for the pi.
Then your repository will be pushed to the pi and the `post-receive` hook on the pi will checkout the (first) branch you have just pushed.

You can now `ssh pi@robo-plot` and test the code you have just pushed in `~/SoftwareDevelopment/Robo-Plot`.
