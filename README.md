# Piscasda API interactive shell

For my current customer I'm communicate with the Piscada Cloud to extract my IoT / controller devices. My IoT / controller devices are basically "black boxes" that are pushing timeseries data to the Piscada Cloud.

Now, Piscada does provide some API documentation. But, since I'm constantly testing / extracting info to debug and just "check" stuff I wanted a simpler way than just have some shell scripts with predefined curl commands.

Therefore I created this "shell". It's mostly created for my own usage - but, maybe it can help others as well.


## Installation

It's a python3 based CLI which also includes its own "python module" that can easily be used by others.

The current best way to install this is:
```
$ git clone https://github.com/asbjorn/piscada-shell
$ cd piscada-shell
$ python3 -mvenv venv
$ source venv/bin/activate
# for Fish shell users -> 'source venv/bin/activate.fish'
$ pip install -r requirements.txt
$ python -mpiscada_shell
```

## References

* Piscada https://piscada.com/

# Author

Myself (asbjorn@fellinghaug.com)
