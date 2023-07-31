I set up Gunicorn to manage the penguin app using Uvicorn as a worker.
The conf is in the gunicorn_conf.py file here.

I used certbot to generate the SSL cert for this droplet, and nginx to forward penguins.firas.casa to my app, which is running by default on port 8000. Look at the nginx config (sites-available with sym link to sites-enabled)

On namecheap an A record was also needed to create a penguins subdomain under firas.casa, and point it to the DO droplet.

The systemd config for penguin classifier: sudo vim /etc/systemd/system/penguin.service 
