# choo-choo
Here's a random train animation synced across connected machines. I had no internet and I was bored :)

Master server:
```
python3 start_master.py
```

Workers (animators) -
Starts a single worker:
```
python3 start_worker.py
```

To start workers on multiple machines, clone this repo on those machines and edit config `MASTER_HOST` to the master machine's IP.

Controller (option 1 - Fetch stats not implemented):
```
python3 controller.py
```


