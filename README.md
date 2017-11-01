crashhub
========

This is a simple web service that aggregates crash reports and opens issues on Github.

Config file
-----------
To start using crashhub, create a `config.json` based on `config.json.example`:

| config key     | value                                                                                                                                                          |
|----------------|----------------------------------------------------------------------------------------------------------------------------------------------------------------|
| db_engine      | Your database engine. Either `postgres`, `mysql` or `sqlite`.                                                                                                  |
| db_name        | The name of the database crashhub should use.                                                                                                                  |
| db_host        | Hostname of the database server. Leave this empty for sqlite.                                                                                                  |
| db_port        | Port of the database server. Leave this empty for sqlite.                                                                                                      |
| db_user        | Name of the database user. Leave this empty for sqlite.                                                                                                        |
| db_password    | Password of the database user. Leave this empty for sqlite.                                                                                                    |
| github_project | The Github project issues should be posted in.                                                                                                                 |
| github_token   | See [:octocat: Creating a personal access token for the command line](https://help.github.com/articles/creating-a-personal-access-token-for-the-command-line/) |

Running crashhub
-------

Database tables will be automatically created once you start crashhub.

### Testing
To run crashhub in a non-production environment (e.g for debugging), simply run `crashhub.py`.


### Production

For an extensive list of options to run crashhub in a high-performance production environment, see [Flask: Deployment Options](http://flask.pocoo.org/docs/0.12/deploying/).

A *:whale: Docker* image that uses uWSGI is available [here](https://hub.docker.com/r/bauerj/crashhub/).
It starts a WSGI server with 2 processes and 2 threads each on port 3031.

This config could be used to deploy it with mariadb and nginx on Docker:

    version: '2'
    services:
      mariadb:
        image: mariadb:latest
        volumes:
            - /var/volumes/mariadb/mysql:/var/lib/mysql
            - /var/volumes/mariadb/conf.d:/etc/mysql/conf.d
      nginx:
        image: nginx
        ports:
          - "80:80"
          - "443:443"
        links:
          - crashhub
        volumes:
          - /var/volumes/nginx/config:/etc/nginx
      crashhub:
        image: bauerj/crashhub
        links:
          - mariadb
        volumes:
          - /var/volumes/crashhub/config.json:/app/config.json

An nginx configuration file could be as simple as this:

    server {
        server_name crashhub.bauerj.eu;
        location / {
            include uwsgi_params;
            uwsgi_pass crashhub:3031;
        }
    }