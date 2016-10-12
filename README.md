rdb-fullstack
=============

Common code for the Relational Databases and Full Stack Fundamentals courses

# Instructions
1. Open vagrant folder in cmd
2. Set up vagrant by running `vagrant up`
3. Log in by running `vagrant ssh`
4. Create database by running `CREATE DATABASE tournament;` in `psql`
5. Use the database by running `psql tournament` and create tables by importing with `\i tournament.sql`
6. Run the test with `python tournament_test.py`